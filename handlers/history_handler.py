from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from services.db import get_search_history
from keyboards.main_keyboard import main_keyboard

router = Router()


@router.message(Command("history"))
async def history_handler(message: types.Message):
    # Используем chat.id, чтобы гарантировать, что сохранялись и извлекаются данные по одному ключу
    history_records = await get_search_history(message.chat.id)

    if not history_records:
        await message.answer("История поиска пуста.", reply_markup=main_keyboard)
        return

    response_lines = ["<b>Ваша история поиска:</b>"]
    for idx, record in enumerate(history_records, start=1):
        # Предполагается, что record содержит: departure, arrival, departure_date, return_date, search_time
        departure, arrival, departure_date, return_date, search_time = record

        # Форматируем время запроса, если это datetime
        if isinstance(search_time, datetime):
            search_time_str = search_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            search_time_str = str(search_time)

        line = f"{idx}. ✈ {departure} → {arrival} | {departure_date}"
        if return_date:
            line += f" → {return_date}"
        line += f"\n    📅 Запрос: {search_time_str}"
        response_lines.append(line)

    response_text = "\n\n".join(response_lines)
    await message.answer(response_text, parse_mode="HTML", reply_markup=main_keyboard)
