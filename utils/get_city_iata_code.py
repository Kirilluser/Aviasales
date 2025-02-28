import logging
import requests


def get_city_iata_code(city_name: str) -> str:
    """
    Получает IATA код для заданного названия города через API автокомплита Travelpayouts.

    :param city_name: Название города, введённое пользователем.
    :return: IATA код города или None, если код не найден.
    """
    url = "https://autocomplete.travelpayouts.com/places2"
    params = {
        "term": city_name,
        "locale": "ru",
        "types[]": "city"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        cities = response.json()
        if cities and isinstance(cities, list):
            logging.info(f"Найденные города для '{city_name}': {cities}")
            # Возвращаем первый найденный IATA код
            return cities[0]["code"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса к autocomplete API: {e}")
    return None
