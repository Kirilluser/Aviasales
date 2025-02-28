from aiogram import Router, types
from aiogram.filters import Command
from services.db import get_search_history
from services.db import store_search_history

router = Router()

@router.message(Command("history"))
@router.callback_query(lambda c: c.data == "history")
async def history_handler(event: types.Message | types.CallbackQuery):
    # Получаем id пользователя из события (для сообщений и callback_query оба используют from_user)
    user_id = event.from_user.id
    from services.db import get_search_history  # Импорт функции получения истории
    history = await get_search_history(user_id)

    if not history:
        text = "История поиска пуста."
    else:
        text = "Ваша история поиска:\n\n"
        for record in history:
            departure, arrival, departure_date, return_date, search_time = record
            return_date_text = f" ➝ {return_date}" if return_date else ""
            text += f"✈ {departure} ➝ {arrival} ({departure_date}{return_date_text})\n📅 {search_time}\n\n"

    if isinstance(event, types.Message):
        await event.answer(text)
    else:
        await event.message.edit_text(text)

# Пример обработчика, где сохраняется история (убедитесь, что здесь используется from_user)
@router.message(Command("search"))
async def search_handler(message: types.Message):
    # Здесь data – пример данных поиска
    data = {
        "departure": "Moscow",
        "arrival": "London",
        "depart_date": "2025-03-10",
        "return_date": "2025-03-20"
    }
    await store_search_history(message.from_user, data)
    await message.answer("Запрос сохранён!")

# Если используете inline-кнопку, убедитесь, что в обработчике callback_query используется event.from_user
@router.callback_query(lambda c: c.data == "search_history")
async def callback_search_history_handler(callback: types.CallbackQuery):
    data = {
        "departure": "Moscow",
        "arrival": "London",
        "depart_date": "2025-03-10",
        "return_date": "2025-03-20"
    }
    await store_search_history(callback.from_user, data)
    await callback.answer("Запрос сохранён!")

