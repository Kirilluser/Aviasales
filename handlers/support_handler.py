from aiogram import Router, types

router = Router()

@router.message(commands=["support"])
async def support_handler(message: types.Message):
    """
    Обрабатывает команду /support и выводит информацию для связи с техподдержкой.
    """
    support_username = "support_username"  # Замените на актуальное имя поддержки.
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Связаться с поддержкой", url=f"tg://resolve?domain={support_username}")]
    ])
    response_text = (
        "Если у вас возникли вопросы или проблемы, свяжитесь с нашим оператором техподдержки. "
        "Нажмите на кнопку ниже, чтобы начать общение."
    )
    await message.answer(response_text, reply_markup=keyboard)
