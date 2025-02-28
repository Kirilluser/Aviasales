from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

personal_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Главное меню"), KeyboardButton(text="⬅ Назад")]
    ],
    resize_keyboard=True
)
