import aiohttp
import logging
from config import FOURSQUARE_API_KEY  # В config

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
                    return f"❌ Места не найдены для запроса «{query}» в {city.title()}."
                result = f"🏛 <b>Места в {city.title()} (запрос: {query}):</b>\n\n"
                for place in places:
                    name = place.get("name", "Неизвестно")
                    location = place.get("location", {})
                    address = location.get("formatted_address", "Адрес не указан")
                    result += f"• <b>{name}</b>\n   {address}\n\n"
                return result
        except Exception as e:
            logging.error(f"Ошибка при получении мест для {city}: {e}")
            return "❌ Ошибка при получении информации о местах."
