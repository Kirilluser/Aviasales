import aiohttp
import logging
from config import AVIASALES_API_KEY
from datetime import datetime
SEARCH_FLIGHTS_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
HOT_DEALS_URL = "https://api.travelpayouts.com/aviasales/v3/get_special_offers"

async def search_flights(origin: str, destination: str, departure_at: str, return_at: str = None) -> str:
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_at,
        "one_way": "true",
        "unique": "false",
        "sorting": "price",
        "direct": "false",
        "currency": "USD",
        "limit": 5,
        "page": 1,
        "token": AVIASALES_API_KEY
    }
    if return_at:
        params["return_at"] = return_at

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(SEARCH_FLIGHTS_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                tickets = data.get("data", [])
                if tickets:
                    result = "🔹 <b>Доступные билеты:</b>\n\n"
                    count = 0
                    for ticket in tickets:
                        airline = ticket.get('airline', 'Неизвестно').upper()
                        price = ticket.get('price', 'Нет данных')
                        departure_time = ticket.get('departure_at', 'Нет данных')[:10]
                        try:
                            departure_date_obj = datetime.strptime(departure_time, "%Y-%m-%d")
                            formatted_date = departure_date_obj.strftime("%d%m")
                        except ValueError:
                            formatted_date = "0000"
                        result += (
                            f"✈ <b>Авиакомпания:</b> {airline}\n"
                            f"📍 <b>Маршрут:</b> {origin} → {destination}\n"
                            f"📅 <b>Дата вылета:</b> {departure_time}\n"
                            f"💰 <b>Цена:</b> {price} USD\n"
                            f"🔗 <a href='https://www.aviasales.com/search/{origin}{formatted_date}{destination}1'>Перейти к покупке</a>\n"
                            f"━━━━━━━━━━━━━━━━━━━\n"
                        )
                        count += 1
                        if count >= 5:  # Ограничение в 5 предложений
                            break
                    return result
                else:
                    return ""
        except Exception as e:
            logging.error(f"Ошибка при поиске билетов: {e}")
            return ""

async def get_hot_deals(origin: str = None, destination: str = None, depart_date: str = None,
                        locale: str = "en", currency: str = "usd") -> list:
    params = {
        "currency": currency,
        "token": AVIASALES_API_KEY
    }
    if origin:
        params["origin"] = origin
    if destination:
        params["destination"] = destination
    if depart_date:  # Добавляем дату, если указана
        params["depart_date"] = depart_date

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.travelpayouts.com/v2/prices/latest", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("data", [])
        except Exception as e:
            logging.error(f"Ошибка при получении горячих предложений: {e}")
            return []

