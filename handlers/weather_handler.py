import aiohttp
import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.filters.state import StateFilter
from config import WEATHER_API  # В config укажите ключ OpenWeatherMap

router = Router()

async def get_weather_for_city(city: str) -> str:
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API,
        "units": "metric",
        "lang": "ru"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                result = (
                    f"⛅ <b>Погода в {city.title()}:</b>\n"
                    f"Температура: {temp}°C\n"
                    f"Описание: {description}\n"
                    f"Влажность: {humidity}%\n"
                    f"Скорость ветра: {wind_speed} м/с"
                )
                return result
        except Exception as e:
            logging.error(f"Ошибка при получении погоды для {city}: {e}")
            return "❌ Не удалось получить данные о погоде."

@router.message(StateFilter("weather:waiting_for_city"), lambda message: bool(message.text and message.text.strip()))
async def weather_command(message: types.Message, state: FSMContext):
    city = message.text.strip()
    logging.info(f"Получение погоды для города: {city}")
    weather_info = await get_weather_for_city(city)
    await message.answer(weather_info, parse_mode="HTML")
    await state.clear()

@router.message(Command("weather"))
async def weather_command_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название города для получения прогноза погоды:")
    # Устанавливаем состояние для ожидания ввода города
    await state.set_state("weather:waiting_for_city")
