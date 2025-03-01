import aiohttp
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from config import FOURSQUARE_API_KEY  # В config

router = Router()
FOURSQUARE_URL = "https://api.foursquare.com/v3/places/search"

async def get_attractions_for_city(city: str, query: str = "attractions", limit: int = 5) -> str:
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "query": query,
        "near": city,
        "limit": limit
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(FOURSQUARE_URL, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                places = data.get("results", [])
                if not places:
                    return f"❌ Достопримечательности не найдены для запроса «{query}» в {city.title()}."
                result = f"🏛 <b>Достопримечательности в {city.title()} (запрос: {query}):</b>\n\n"
                for place in places:
                    name = place.get("name", "Неизвестно")
                    location = place.get("location", {})
                    address = location.get("formatted_address", "Адрес не указан")
                    result += f"• <b>{name}</b>\n   {address}\n\n"
                return result
        except Exception as e:
            logging.error(f"Ошибка при получении достопримечательностей для {city}: {e}")
            return "❌ Ошибка при получении информации о достопримечательностях."

@router.message(StateFilter("attractions:waiting_for_city"), lambda message: bool(message.text and message.text.strip()))
async def attractions_command(message: types.Message, state: FSMContext):
    # Расширяем ввод: разделяем по запятой
    parts = [part.strip() for part in message.text.split(",")]
    city = parts[0]
    query = parts[1] if len(parts) >= 2 and parts[1] else "attractions"
    try:
        limit = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 5
    except Exception:
        limit = 5

    logging.info(f"Получение достопримечательностей для города: {city} с запросом: {query} и лимитом: {limit}")
    attractions_info = await get_attractions_for_city(city, query, limit)
    await message.answer(attractions_info, parse_mode="HTML")
    await state.clear()

@router.message(Command("attractions"))
async def attractions_command_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите название города для получения информации о местах.\n\n"
        "Формат ввода:\n"
        "• <b>город</b>\n"
        "• или <b>город, категория</b>\n"
        "• или <b>город, категория, лимит</b>\n\n"
        "Например: <i>Москва, музеи, 10</i>",
        parse_mode="HTML"
    )
    await state.set_state("attractions:waiting_for_city")
