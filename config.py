import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токены и ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
AVIASALES_API_KEY = os.getenv("AVIASALES_API_KEY")
WEATHER_API =  os.getenv("WEATHER_API")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")
# Настройки подключения к PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
