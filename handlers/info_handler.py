from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("info"))
async def info_handler(message: types.Message):
    text = (
        "Добро пожаловать в раздел <b>Инфо</b>!\n\n"
        "Здесь вы найдете полезные материалы для путешественников.\n\n"
        "Выберите нужный раздел:"
    )
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Полезные статьи", url="https://happy-travel.kz/article/")],
        [types.InlineKeyboardButton(text="Гид", url="https://planetofhotels.com/guide/ru")],
        [types.InlineKeyboardButton(text="Полезные ресурсы", callback_data="info:resources")]
    ])
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
#
@router.callback_query(lambda c: c.data == "info:resources")
async def info_resources_handler(callback: types.CallbackQuery):
    resources_text = (
        "<b>Полезные ресурсы для путешественников:</b>\n\n"
        "• <a href='https://www.booking.com/'>Booking.com</a> – бронирование отелей и апартаментов.\n"
        "• <a href='https://www.airbnb.com/'>Airbnb</a> – аренда жилья по всему миру.\n"
        "• <a href='https://www.skyscanner.ru/'>Skyscanner</a> – поиск дешевых авиабилетов.\n"
        "• <a href='https://www.agoda.com/'>Agoda</a> – бронирование гостиниц, особенно в Азии.\n"
        "• <a href='https://www.expedia.com/'>Expedia</a> – комплексный сервис для планирования путешествия.\n"
        "• <a href='https://www.tripadvisor.ru/'>TripAdvisor</a> – отзывы и рекомендации путешественников.\n"
        "• <a href='https://www.google.com/maps'>Google Maps</a> – карты и навигация.\n"
        "• <a href='https://www.lonelyplanet.com/'>Lonely Planet</a> – путеводители и советы путешественников.\n"
        "• <a href='https://www.rome2rio.com/'>Rome2rio</a> – маршруты и варианты транспорта.\n"
        "• <a href='https://www.hopper.com/'>Hopper</a> – прогнозы цен на авиабилеты и отели.\n"
        "• <a href='https://www.kayak.com/'>Kayak</a> – поиск и сравнение цен на билеты и отели.\n"
        "• <a href='https://www.trip.com/'>Trip.com</a> – бронирование, скидки и акции.\n"
        "• <a href='https://www.travelzoo.com/'>Travelzoo</a> – эксклюзивные предложения на путешествия.\n"
    )
    await callback.message.answer(resources_text, parse_mode="HTML")
    await callback.answer()
