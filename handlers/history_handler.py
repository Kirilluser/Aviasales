from datetime import datetime
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_keyboard import main_keyboard
from services.db import get_search_history, clear_search_history
import logging

router = Router()

async def build_history_text(chat_id: int) -> str:
    history_records = await get_search_history(chat_id)
    if not history_records:
        return "История поиска пуста."
    response_lines = ["<b>Ваша история поиска:</b>"]
    for idx, record in enumerate(history_records, start=1):
        # Ожидается, что record содержит: departure, arrival, departure_date, return_date, search_time
        departure, arrival, departure_date, return_date, search_time = record
        if isinstance(search_time, datetime):
            search_time_str = search_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            search_time_str = str(search_time)
        line = f"{idx}. ✈ {departure} → {arrival} | {departure_date}"
        if return_date:
            line += f" → {return_date}"
        line += f"\n   📅 Запрос: {search_time_str}"
        response_lines.append(line)
    return "\n\n".join(response_lines)

@router.message(lambda message: message.text == "📃 История")
async def navigation_history_handler(message: types.Message):
    text = await build_history_text(message.chat.id)
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить", callback_data="history")],
        [InlineKeyboardButton(text="Очистить историю", callback_data="clear_history")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=inline_kb)

@router.callback_query(lambda c: c.data == "history")
async def history_callback_handler(callback: types.CallbackQuery):
    text = await build_history_text(callback.message.chat.id)
    # Сохраняем текущую inline-клавиатуру, чтобы кнопки остались (либо можно задать новую)
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить", callback_data="history")],
        [InlineKeyboardButton(text="Очистить историю", callback_data="clear_history")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=inline_kb)
    await callback.answer("История обновлена")

@router.callback_query(lambda c: c.data == "clear_history")
async def clear_history_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    logging.info("Очистка истории для чата: %s", chat_id)
    await clear_search_history(chat_id)
    logging.info("История для чата %s очищена", chat_id)
    await callback.message.edit_text("История поиска очищена.", reply_markup=None)
    await callback.answer("История очищена")
    # Отправляем сообщение с основным меню
    await callback.message.answer("Главное меню:", reply_markup=main_keyboard)

