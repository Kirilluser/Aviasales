import aiohttp
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from config import FOURSQUARE_API_KEY  # В config

router = Router()
# функция поиска достопримечательностей
async def get_attractions_for_city(city: str) -> str:
    base_url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "query": "attractions",
        "near": city,
        "limit": 5
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, headers=headers, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                places = data.get("results", [])
                if not places:
                    return "❌ Достопримечательности не найдены."
                result = f"🏛 <b>Достопримечательности в {city.title()}:</b>\n\n"
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
    city = message.text.strip()
    logging.info(f"Получение достопримечательностей для города: {city}")
    attractions_info = await get_attractions_for_city(city)
    await message.answer(attractions_info, parse_mode="HTML")
    await state.clear()

@router.message(Command("attractions"))
async def attractions_command_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название города для получения информации о достопримечательностях:")
    await state.set_state("attractions:waiting_for_city")
