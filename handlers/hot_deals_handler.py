import logging
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from services.aviasales import get_hot_deals
from utils.get_city_iata_code import get_city_iata_code

router = Router()

# Основной обработчик команды /hotdeals
@router.message(Command("hotdeals"))
async def hot_deals_handler(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="По числу", callback_data="hotdeals:by_date"),
            types.InlineKeyboardButton(text="По городу", callback_data="hotdeals:by_city")
        ]
    ])
    await state.clear()
    await message.answer("Выберите способ получения горячих предложений:", reply_markup=keyboard)

# ===== Поток "По числу" (выбор даты через календарь) =====
@router.callback_query(lambda c: c.data == "hotdeals:by_date")
async def hot_deals_by_date(callback: types.CallbackQuery, state: FSMContext):
    from utils.calendar import generate_calendar
    today = datetime.today()
    calendar_markup = generate_calendar(today.year, today.month)
    await state.clear()
    await callback.message.answer("Выберите дату вылета:", reply_markup=calendar_markup)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("CALENDAR:"), StateFilter(None))
async def process_date_callback(callback: types.CallbackQuery, state: FSMContext):
    selected_date = callback.data.split(":", 1)[1]  # формат YYYY-MM-DD
    logging.info(f"Выбрана дата: {selected_date}")
    try:
        # Получаем все предложения (без фильтра по городу)
        deals = await get_hot_deals()
        logging.info(f"Все предложения от API: {deals}")

        # Фильтруем по точной дате
        filtered_deals = [d for d in deals if d.get("depart_date") == selected_date]

        # Если точных совпадений нет, находим ближайшие варианты по дате
        if not filtered_deals:
            try:
                sorted_deals = sorted(
                    deals,
                    key=lambda d: (
                        abs((datetime.strptime(d["depart_date"], "%Y-%m-%d") - datetime.strptime(selected_date, "%Y-%m-%d")).days),
                        d.get("value", float('inf'))
                    )
                )
                filtered_deals = sorted_deals[:5]  # берем 5 ближайших вариантов
            except Exception as ex:
                logging.error(f"Ошибка при сортировке по дате: {ex}")
                filtered_deals = []

        logging.info(f"Отфильтрованные предложения: {filtered_deals}")

        if not filtered_deals:
            await callback.message.answer("❌ Нет доступных горячих предложений на указанную дату.")
            await callback.answer()
            return

        # Сортируем варианты по цене (используем поле "value")
        sorted_deals = sorted(filtered_deals, key=lambda d: d.get("value", float('inf')))
        response = f"🔥 <b>Лучшие предложения на {selected_date}:</b>\n\n"
        for deal in sorted_deals[:5]:
            # Используем gate как оператора, value как цену
            operator = deal.get("gate", "Неизвестно").upper()
            price = deal.get("value", "Нет данных")
            depart_date = deal.get("depart_date", "Нет данных")
            origin = deal.get("origin", "??")
            destination = deal.get("destination", "??")
            response += (
                f"✈ <b>Оператор:</b> {operator}\n"
                f"📍 <b>Маршрут:</b> {origin} → {destination}\n"
                f"📅 <b>Дата вылета:</b> {depart_date}\n"
                f"💰 <b>Цена:</b> {price} USD\n"
                f"🔗 <a href='https://www.aviasales.com/search/{origin}{destination}{depart_date.replace('-', '')}'>Перейти к покупке</a>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
            )
        await callback.message.answer(response, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при поиске горячих предложений: {e}")
        await callback.message.answer("⚠ Произошла ошибка при получении данных. Попробуйте позже.")
    await callback.answer()

# ===== Поток "По городу" =====
@router.callback_query(lambda c: c.data == "hotdeals:by_city")
async def hot_deals_by_city(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Введите город отправления для горячих предложений (например, Москва):")
    await state.set_state("hotdeals:by_city")
    await callback.answer()

@router.message(StateFilter("hotdeals:by_city"))
async def process_hot_deals_by_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    iata_code = get_city_iata_code(city)
    if not iata_code:
        await message.answer("❌ Ошибка! Не удалось найти IATA-код для этого города. Попробуйте снова.")
        return
    await state.update_data(city=iata_code)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=str(n), callback_data=f"hotdeals:city:number:{n}") for n in range(1, 6)]
    ])
    await message.answer("Сколько предложений вы хотите увидеть (от 1 до 5)?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("hotdeals:city:number:"), StateFilter("hotdeals:by_city"))
async def process_hot_deals_city_number(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    count = int(parts[3])
    data = await state.get_data()
    city_code = data.get("city")
    if not city_code:
        await callback.message.answer("❌ Ошибка: город не найден.")
        await state.clear()
        return
    try:
        deals = await get_hot_deals(origin=city_code)
        logging.info(f"Горячие предложения для {city_code}: {deals}")
        if not deals:
            await callback.message.answer("❌ Горячие предложения не найдены для указанного города.")
            await callback.answer()
            return
        sorted_deals = sorted(deals, key=lambda d: d.get("value", float('inf')))
        selected_deals = sorted_deals[:count]
        response = f"🔥 <b>Горячие предложения для {city_code}:</b>\n\n"
        for deal in selected_deals:
            operator = deal.get("gate", "Неизвестно").upper()
            price = deal.get("value", "Нет данных")
            depart_date = deal.get("depart_date", "Нет данных")
            origin = deal.get("origin", city_code)
            destination = deal.get("destination", "??")
            response += (
                f"✈ <b>Оператор:</b> {operator}\n"
                f"📍 <b>Маршрут:</b> {origin} → {destination}\n"
                f"📅 <b>Дата вылета:</b> {depart_date}\n"
                f"💰 <b>Цена:</b> {price} USD\n"
                f"🔗 <a href='https://www.aviasales.com/search/{origin}{destination}{depart_date.replace('-', '')}'>Перейти к покупке</a>\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
            )
        await callback.message.answer(response, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка при получении горячих предложений: {e}")
        await callback.message.answer("⚠ Произошла ошибка при загрузке данных.")
    await state.clear()
    await callback.answer()
