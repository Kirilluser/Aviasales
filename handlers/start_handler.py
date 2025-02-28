from aiogram import Router, types
from aiogram.filters import Command
from services.db import ensure_user_exists  # Функция для вставки пользователя
from keyboards.main_keyboard import main_keyboard  # Импортируем клавиатуру

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    await ensure_user_exists(message.from_user)
    await message.answer(
        "Привет! Я бот Aviasales.\nЯ здесь, чтобы помочь тебе быстро и удобно найти и забронировать авиабилеты по самым выгодным ценам.\nПросто укажи город отправления и город назначения, а я подберу для тебя оптимальные варианты.\n\nЕсли потребуется помощь, набери /help",
        reply_markup=main_keyboard  # Добавляем клавиатуру
    )