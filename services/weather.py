import aiohttp
import logging
from config import WEATHER_API # Добавьте в config свой API-ключ

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

async def get_weather_for_city(city: str) -> str:
    params = {
        "q": city,
        "appid": WEATHER_API,
        "units": "metric",
        "lang": "ru"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(WEATHER_URL, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            # Формируем текст с погодой
            description = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            result = (
                f"🌡 Погода в {city}:\n"
                f"Описание: {description}\n"
                f"Температура: {temp}°C\n"
                f"Влажность: {humidity}%\n"
                f"Скорость ветра: {wind_speed} м/с"
            )
            return result
