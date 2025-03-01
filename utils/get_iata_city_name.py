import logging
import requests


def get_city_name_from_iata(iata_code: str) -> str:
    """
    Получает полное название города по IATA-коду через API автокомплита Travelpayouts.

    :param iata_code: Трёхбуквенный IATA-код города.
    :return: Полное название города или None, если не найден.
    """
    url = "https://autocomplete.travelpayouts.com/places2"
    params = {
        "term": iata_code,  # ищем по коду
        "locale": "ru",  # русская локаль
        "types[]": "city"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        cities = response.json()
        if cities and isinstance(cities, list):
            # Ищем точное совпадение по IATA-коду (без учета регистра)
            for city in cities:
                if city.get("code", "").upper() == iata_code.upper():
                    return city.get("name")
            # Если точного совпадения нет, возвращаем название первого найденного города
            return cities[0].get("name")
    except requests.RequestException as e:
        logging.error(f"Ошибка запроса к API автокомплита: {e}")
    return None


# Пример использования:
if __name__ == "__main__":
    code = "NQZ"  # пример IATA-кода
    city_name = get_city_name_from_iata(code)
    if city_name:
        print(f"IATA {code} соответствует городу: {city_name}")
    else:
        print("Город по заданному IATA коду не найден")
