from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.aviasales import search_flights
from services.db import store_search_history
from utils.get_city_iata_code import get_iata  # асинхронная функция для получения IATA

router = Router()

class FlightSearch(StatesGroup):
    departure = State()
    arrival = State()
    depart_date = State()
    return_date = State()

@router.message(commands=["search"])
async def search_start(message: types.Message, state: FSMContext):
    await message.answer("Введите город отправления (например, Москва):")
    await state.set_state(FlightSearch.departure)

@router.message(state=FlightSearch.departure)
async def process_departure(message: types.Message, state: FSMContext):
    city_name = message.text.strip()
    iata = await get_iata(city_name)
    if not iata:
        await message.answer("Город не найден или отсутствует IATA код. Попробуйте еще раз.")
        return
    await state.update_data(departure=iata)
    await message.answer("Введите город прибытия (например, Париж):")
    await state.set_state(FlightSearch.arrival)

@router.message(state=FlightSearch.arrival)
async def process_arrival(message: types.Message, state: FSMContext):
    city_name = message.text.strip()
    iata = await get_iata(city_name)
    if not iata:
        await message.answer("Город не найден или отсутствует IATA код. Попробуйте еще раз.")
        return
    await state.update_data(arrival=iata)
    await message.answer("Введите дату вылета (формат YYYY-MM-DD):")
    await state.set_state(FlightSearch.depart_date)

@router.message(state=FlightSearch.depart_date)
async def process_depart_date(message: types.Message, state: FSMContext):
    await state.update_data(depart_date=message.text.strip())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Добавить дату возвращения", callback_data="add_return_date"),
            types.InlineKeyboardButton(text="Пропустить", callback_data="skip_return_date")
        ]
    ])
    await message.answer("Хотите указать дату возвращения?", reply_markup=keyboard)
    await state.set_state(FlightSearch.return_date)

@router.callback_query(lambda c: c.data in ["add_return_date", "skip_return_date"], state=FlightSearch.return_date)
async def process_return_date_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "add_return_date":
        await callback.message.answer("Введите дату возвращения (формат YYYY-MM-DD):")
    else:
        await state.update_data(return_date=None)
        await finalize_search(callback.message, state)
    await callback.answer()

@router.message(state=FlightSearch.return_date)
async def process_return_date(message: types.Message, state: FSMContext):
    await state.update_data(return_date=message.text.strip())
    await finalize_search(message, state)

async def finalize_search(message: types.Message, state: FSMContext):
    data = await state.get_data()
    departure = data.get("departure")
    arrival = data.get("arrival")
    depart_date = data.get("depart_date")
    return_date = data.get("return_date")

    confirmation = (
        f"Поиск билетов:\nОткуда: {departure}\nКуда: {arrival}\nДата вылета: {depart_date}\n"
        f"Дата возвращения: {return_date if return_date else 'не указана'}"
    )
    await message.answer(confirmation + "\nИдет поиск...")

    flights = await search_flights(departure, arrival, depart_date, return_date)
    if flights:
        result_text = "Найденные билеты:\n\n"
        for flight in flights:
            route = f"{flight.get('origin', '')} -> {flight.get('destination', '')}"
            date = flight.get("depart_date", "не указана")
            price = flight.get("value", "не указана")
            ticket_url = flight.get("link", "#")
            result_text += (
                f"Маршрут: {route}\nДата: {date}\nЦена: {price}\n"
                f"<a href='{ticket_url}'>Купить билет</a>\n\n"
            )
        await message.answer(result_text, parse_mode="HTML")
    else:
        await message.answer("К сожалению, билеты не найдены.")
        await store_search_history(message.from_user, data)
        await state.clear()

