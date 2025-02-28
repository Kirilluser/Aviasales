import aiohttp
import logging
from config import FOURSQUARE_API_KEY  # Добавьте в config

FOURSQUARE_URL = "https://api.foursquare.com/v3/places/search"

async def get_attractions_for_city(city: str) -> str:
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "query": "достопримечательности",
        "near": city,
        "limit": 5
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(FOURSQUARE_URL, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            results = data.get("results", [])
            if not results:
                return "❌ Не удалось найти достопримечательности для указанного города."
            response_text = f"📍 <b>Достопримечательности в {city}:</b>\n\n"
            for place in results:
                name = place.get("name", "Неизвестно")
                location = place.get("location", {})
                address = location.get("formatted_address", "Адрес не указан")
                response_text += f"• {name}\n   {address}\n\n"
            return response_text
