import logging
from datetime import datetime, timedelta, date
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.aviasales import search_flights
from services.db import store_search_history
from utils.get_city_iata_code import get_city_iata_code
from utils.calendar import generate_calendar

router = Router()

class FlightSearch(StatesGroup):
    departure_city = State()
    arrival_city = State()
    ticket_type = State()       # "fixed" или "flexible"
    departure_date = State()    # для фиксированного режима
    flexible_range = State()    # количество дней гибкости (например, 3)
    flexible_date = State()     # базовая дата для гибкого поиска
    return_choice = State()
    return_date = State()

@router.message(Command("find_ticket"))
async def search_flight_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите город отправления (например, Москва):")
    await state.set_state(FlightSearch.departure_city)

@router.message(StateFilter(FlightSearch.departure_city))
async def process_departure_city(message: types.Message, state: FSMContext):
    iata_code = get_city_iata_code(message.text)
    if not iata_code:
        await message.answer("Ошибка! Не удалось найти IATA-код для этого города. Попробуйте снова.")
        return
    await state.update_data(departure_city=iata_code)
    await message.answer("Введите город прибытия (например, Париж):")
    await state.set_state(FlightSearch.arrival_city)

@router.message(StateFilter(FlightSearch.arrival_city))
async def process_arrival_city(message: types.Message, state: FSMContext):
    iata_code = get_city_iata_code(message.text)
    if not iata_code:
        await message.answer("Ошибка! Не удалось найти IATA-код для этого города. Попробуйте снова.")
        return
    await state.update_data(arrival_city=iata_code)
    # Предлагаем выбрать тип билета: фиксированный или гибкий
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Фиксированный", callback_data="ticket_type:fixed"),
            types.InlineKeyboardButton(text="Гибкий", callback_data="ticket_type:flexible")
        ]
    ])
    await message.answer("Выберите тип билета:", reply_markup=keyboard)
    await state.set_state(FlightSearch.ticket_type)

@router.callback_query(lambda c: c.data and c.data.startswith("ticket_type:"), StateFilter(FlightSearch.ticket_type))
async def process_ticket_type(callback: types.CallbackQuery, state: FSMContext):
    ticket_type = callback.data.split(":")[1]
    await state.update_data(ticket_type=ticket_type)
    if ticket_type == "fixed":
        today = datetime.today().date()
        calendar_markup = generate_calendar(today.year, today.month)
        await callback.message.answer("Выберите дату вылета (только будущие даты):", reply_markup=calendar_markup)
        await state.set_state(FlightSearch.departure_date)
    else:
        # Гибкий режим – спрашиваем диапазон гибкости
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=str(n), callback_data=f"flexible:range:{n}") for n in range(1, 8)]
        ])
        await callback.message.answer("Выберите гибкий диапазон (количество дней ±):", reply_markup=keyboard)
        await state.set_state(FlightSearch.flexible_range)
    await callback.answer()

# --- Фиксированный режим поиска билетов ---
@router.callback_query(lambda c: c.data and c.data.startswith("CALENDAR:"), StateFilter(FlightSearch.departure_date))
async def process_fixed_departure_date(callback: types.CallbackQuery, state: FSMContext):
    selected_date_str = callback.data.split(":", 1)[1]  # формат YYYY-MM-DD
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    today = datetime.today().date()
    if selected_date < today:
        await callback.message.answer("❌ Выбранная дата уже прошла. Пожалуйста, выберите будущую дату.")
        await callback.answer()
        return
    await state.update_data(departure_date=selected_date_str)
    await callback.message.answer(f"Вы выбрали дату вылета: {selected_date_str}")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Добавить дату возвращения", callback_data="add_return_date"),
            types.InlineKeyboardButton(text="Билет в один конец", callback_data="one_way")
        ]
    ])
    await callback.message.answer("Выберите тип билета:", reply_markup=keyboard)
    await state.set_state(FlightSearch.return_choice)
    await callback.answer()

@router.callback_query(lambda c: c.data in ["add_return_date", "one_way"], StateFilter(FlightSearch.return_choice))
async def return_choice_handler(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "add_return_date":
        await state.set_state(FlightSearch.return_date)
        today = datetime.today().date()
        calendar_markup = generate_calendar(today.year, today.month)
        await callback.message.answer("Выберите дату возвращения (не раньше даты вылета):", reply_markup=calendar_markup)
    else:
        await state.update_data(return_date=None)
        await finalize_search(callback.message, state)
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("CALENDAR:"), StateFilter(FlightSearch.return_date))
async def process_return_date_callback(callback: types.CallbackQuery, state: FSMContext):
    selected_date_str = callback.data.split(":", 1)[1]
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    data = await state.get_data()
    departure_date_str = data.get("departure_date")
    if departure_date_str:
        departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
        if selected_date < departure_date:
            await callback.message.answer("❌ Дата возвращения не может быть раньше даты вылета.")
            await callback.answer()
            return
    await state.update_data(return_date=selected_date_str)
    await callback.message.answer(f"Вы выбрали дату возвращения: {selected_date_str}")
    await finalize_search(callback.message, state)
    await callback.answer()

# --- Гибкий режим поиска билетов ---
@router.callback_query(lambda c: c.data and c.data.startswith("flexible:range:"), StateFilter(FlightSearch.flexible_range))
async def process_flexible_range(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    flex_range = int(parts[2])
    await state.update_data(flexible_range=flex_range)
    today = datetime.today().date()
    calendar_markup = generate_calendar(today.year, today.month)
    await callback.message.answer("Выберите базовую дату вылета (будущую дату):", reply_markup=calendar_markup)
    await state.set_state(FlightSearch.flexible_date)
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("CALENDAR:"), StateFilter(FlightSearch.flexible_date))
async def process_flexible_date(callback: types.CallbackQuery, state: FSMContext):
    base_date_str = callback.data.split(":", 1)[1]
    base_date = datetime.strptime(base_date_str, "%Y-%m-%d").date()
    today = datetime.today().date()
    if base_date < today:
        await callback.message.answer("❌ Выбранная базовая дата уже прошла. Пожалуйста, выберите будущую дату.")
        await callback.answer()
        return
    await state.update_data(flexible_date=base_date_str)
    data = await state.get_data()
    flex_range = data.get("flexible_range", 0)
    results = []
    # Ищем билеты для каждого дня в диапазоне base_date ± flex_range
    for delta in range(-flex_range, flex_range + 1):
        current_date = base_date + timedelta(days=delta)
        if current_date < today:
            continue
        date_str = current_date.isoformat()
        info = await search_flights(
            origin=data['departure_city'],
            destination=data['arrival_city'],
            departure_at=date_str,
            return_at=data.get('return_date')
        )
        if info:
            results.append(info)
    if results:
        response = "🔥 <b>Гибкие предложения:</b>\n\n" + "\n".join(results)
        await callback.message.answer(response, parse_mode="HTML")
    else:
        await callback.message.answer("⚠ Билеты не найдены в выбранном диапазоне.")
    await state.clear()
    await callback.answer()

async def finalize_search(message: types.Message, state: FSMContext):
    data = await state.get_data()
    flight_info = await search_flights(
        origin=data['departure_city'],
        destination=data['arrival_city'],
        departure_at=data['departure_date'],
        return_at=data.get('return_date')
    )
    if flight_info:
        await message.answer(f"Найденные билеты:\n{flight_info}", parse_mode="HTML")
    else:
        await message.answer("⚠ Билеты не найдены. Попробуйте изменить параметры поиска.")
    await store_search_history(message.from_user.id, data)
    await state.clear()
