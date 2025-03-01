from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✈ Найти билет"), KeyboardButton(text="🔥 Горячие предложения")],
        [KeyboardButton(text="👤 Личный кабинет"), KeyboardButton(text="📃 История"), KeyboardButton(text="⚙ Поддержка")],
        [KeyboardButton(text="ℹ Инфо"),KeyboardButton(text="⛅Погода")],
        [KeyboardButton(text="📍Места")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
