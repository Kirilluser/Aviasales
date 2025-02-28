import logging
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from utils.calendar import generate_calendar

logging.basicConfig(level=logging.INFO)

router = Router()

@router.message(Command("calendar"))
async def show_calendar(message: types.Message):
    """
    Отправляет пользователю календарь для выбора даты.
    """
    today = datetime.today()
    calendar_markup = generate_calendar(today.year, today.month)
    await message.answer("Выберите дату:", reply_markup=calendar_markup)

@router.callback_query(lambda c: c.data and c.data.startswith("CALENDAR:"))
async def process_calendar_date(callback: types.CallbackQuery):
    """
    Обрабатывает выбор даты из календаря и отправляет выбранную дату пользователю.
    """
    selected_date = callback.data.split(":", 1)[1]
    await callback.message.answer(f"Вы выбрали дату: {selected_date}")
    await callback.answer()

@router.callback_query(lambda c: c.data and c.data.startswith("CALENDAR_NAV:"))
async def process_calendar_navigation(callback: types.CallbackQuery):
    """
    Обрабатывает навигацию по календарю (переключение месяцев) и обновляет сообщение.
    """
    logging.info(f"Навигация календаря: {callback.data}")  # Логируем вызов

    try:
        _, direction, new_date = callback.data.split(":")
        year, month = map(int, new_date.split("-"))

        new_calendar = generate_calendar(year, month)

        # Обновляем сообщение с новым календарем
        await callback.message.edit_reply_markup(reply_markup=new_calendar)
        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка при обновлении календаря: {e}")
        await callback.message.answer("Ошибка обновления календаря.")
        await callback.answer()

@router.callback_query(lambda c: c.data == "IGNORE")
async def ignore_callback(callback: types.CallbackQuery):
    """
    Обрабатывает callback-кнопки, которые не требуют действия.
    """
    await callback.answer()
