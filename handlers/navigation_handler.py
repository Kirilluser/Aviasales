from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from handlers.flight_search_handler import search_flight_start
from handlers.hot_deals_handler import hot_deals_handler
from handlers.info_handler import info_handler
from handlers.weather_handler import weather_command
from handlers.attractions_handler import attractions_command
from handlers.profile_handler import profile_handler
from keyboards.main_keyboard import main_keyboard
from services.db import get_search_history
from datetime import datetime
router = Router()

@router.message(lambda message: message.text == "✈ Найти билет")
async def find_ticket_via_button(message: types.Message, state: FSMContext):
    # Запускаем процесс поиска билетов напрямую, вызывая обработчик поиска
    await search_flight_start(message, state)

@router.message(lambda message: message.text == "🔥 Горячие предложения")
async def hot_deals_via_button(message: types.Message, state: FSMContext):
    # Запускаем процесс горячих предложений напрямую
    await hot_deals_handler(message, state)

@router.message(lambda message: message.text == "👤 Личный кабинет")
async def profile_via_button(message: types.Message, state: FSMContext):
    # Запускаем личный кабинет напрямую
    await profile_handler(message)
@router.message(lambda message: message.text == "ℹ Инфо")
async def info_via_button(message: types.Message, state: FSMContext):
    await info_handler(message)


@router.message(lambda message: message.text == "📃 История")
async def navigation_history_handler(message: types.Message):
    # Используем идентификатор чата для получения истории
    history_records = await get_search_history(message.chat.id)

    if not history_records:
        await message.answer("История поиска пуста.", reply_markup=main_keyboard)
        return

    response_lines = ["<b>Ваша история поиска:</b>"]
    for idx, record in enumerate(history_records, start=1):
        # Ожидается, что record содержит следующие поля:
        # departure, arrival, departure_date, return_date, search_time
        departure, arrival, departure_date, return_date, search_time = record

        # Форматируем время запроса, если это объект datetime
        if isinstance(search_time, datetime):
            search_time_str = search_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            search_time_str = str(search_time)

        line = f"{idx}. ✈ {departure} → {arrival} | {departure_date}"
        if return_date:
            line += f" → {return_date}"
        line += f"\n   📅 Запрос: {search_time_str}"
        response_lines.append(line)

    response_text = "\n\n".join(response_lines)
    await message.answer(response_text, parse_mode="HTML", reply_markup=main_keyboard)
@router.message(lambda message: message.text == "⛅Погода")
async def weather_button_handler(message: types.Message, state: FSMContext):
    # Сбрасываем состояние, чтобы не было конфликтов
    await state.clear()
    await message.answer("Введите название города для получения прогноза погоды:")
    # Устанавливаем новое состояние для дальнейшего ввода города
    await state.set_state("weather:waiting_for_city")

@router.message(lambda message: message.text == "📍Достопримечательности")
async def attractions_button_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название города для получения информации о достопримечательностях:")
    await state.set_state("attractions:waiting_for_city")

@router.message(lambda message: message.text == "⚙ Поддержка")
async def support_via_button(message: types.Message):
    await message.answer("Наш бот — плод труда настоящего энтузиаста, вдохновлённого идеей сделать путешествия доступными для каждого. Мы неустанно совершенствуем наш сервис, чтобы поиск лучших авиабилетов был максимально простым и быстрым для вас.\nБлагодарим, что остаетесь с нами!\nКонтакты службы поддержки:\n      🆔@NarrativeLive\n      🔗+77710007777\n      📬kolomieckirill38@gmail.com\n      📍ул. Чернышевского, 59",reply_markup=main_keyboard)
    resources_text = (
        "<b>Соц сети автора:</b>\n"
        "• <a href='https://t.me/NarrativeLive'>Telegram</a>\n"
        "• <a href='https://www.linkedin.com/in/kirill-kolomiyets-ab2a9a2b5/'>LinkedIn</a>\n"
        "• <a href='https://github.com/Kirilluser'>GitHub</a>\n"
        "• <a href='https://x.com/Narrative_Live'>Twitter</a>\n"

    )
    await message.answer(resources_text, parse_mode="HTML")

