from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def help_handler(message: types.Message):
    help_text = (
        "Доступные команды:\n"
        "/start - Запустить бота и показать главное меню\n"
        "/find_ticket - Поиск авиабилетов\n"
        "/hotdeals - Горячие предложения\n"
        "/help - Список доступных команд\n\n"

    )
    await message.answer(help_text)
