from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from handlers.flight_search_handler import search_flight_start
from handlers.hot_deals_handler import hot_deals_handler
from handlers.info_handler import info_handler
from handlers.weather_handler import weather_command
from handlers.attractions_handler import attractions_command
from handlers.profile_handler import profile_handler
from keyboards.main_keyboard import main_keyboard
from keyboards.personal_keyboard import personal_keyboard
import json

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
async def history_via_button(message: types.Message):
    # Читаем историю запросов из файла history.json
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
        user_history = history.get(str(message.from_user.id), "История пуста.")
        await message.answer(f"История запросов:\n{user_history}", reply_markup=main_keyboard)
    except Exception:
        await message.answer("История пуста.", reply_markup=main_keyboard)

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

