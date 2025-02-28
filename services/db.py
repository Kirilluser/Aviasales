import asyncpg
import logging
from datetime import date
from aiogram import types
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Глобальный объект пула соединений
pool = None

async def init_db_pool():
    """
    Инициализирует пул соединений к PostgreSQL и создаёт таблицы users и search_history, если они отсутствуют.
    Вызывайте эту функцию при старте приложения (например, в bot.py).
    """
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        logging.info("Соединение с PostgreSQL установлено.")
        async with pool.acquire() as connection:
            # Создаём таблицу пользователей
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    language_code TEXT
                );
            """)
            logging.info("Таблица 'users' создана или уже существует.")

            # Создаём таблицу истории запросов
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    departure TEXT NOT NULL,
                    arrival TEXT NOT NULL,
                    departure_date DATE NOT NULL,
                    price INTEGER,
                    airline TEXT,
                    link TEXT,
                    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    return_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            """)
            logging.info("Таблица 'search_history' создана или уже существует.")
    except Exception as e:
        logging.error(f"Ошибка при подключении к PostgreSQL: {e}")

async def ensure_user_exists(user):
    """
    Проверяет, существует ли пользователь в таблице users.
    Если передан объект User, добавляет его при отсутствии.
    Если передан целочисленный id, добавляет запись с дефолтными значениями, если записи нет.
    """
    if pool is None:
        logging.error("Пул соединений не инициализирован.")
        return

    async with pool.acquire() as connection:
        if isinstance(user, int):
            user_id = user
            logging.info(f"Проверка пользователя: {user_id}")
            result = await connection.fetchrow("SELECT user_id FROM users WHERE user_id = $1;", user_id)
            if not result:
                # Вставляем запись с дефолтными значениями
                await connection.execute("""
                    INSERT INTO users(user_id, full_name, username, language_code)
                    VALUES($1, $2, $3, $4);
                """, user_id, "Unknown", "Unknown", "unknown")
                logging.info("Новый пользователь добавлен с дефолтными значениями: %s", user_id)
        else:
            user_id = user.id
            logging.info(f"Проверка пользователя: {user.id} - {user.full_name}")
            result = await connection.fetchrow("SELECT user_id FROM users WHERE user_id = $1;", user_id)
            if not result:
                await connection.execute("""
                    INSERT INTO users(user_id, full_name, username, language_code)
                    VALUES($1, $2, $3, $4);
                """, user_id, user.full_name, user.username, user.language_code)
                logging.info("Новый пользователь добавлен: %s", user_id)
            else:
                logging.info("Пользователь %s уже существует.", user_id)

async def store_search_history(user, query_data: dict):
    """
    Сохраняет историю запроса пользователя в базу данных.
    Всегда проверяет, что пользователь существует в таблице users.
    Ожидается, что query_data содержит данные с ключами:
      - "departure" или "departure_city"
      - "arrival" или "arrival_city"
      - "depart_date" или "departure_date" (формат ISO: YYYY-MM-DD)
      - "return_date" (опционально, формат ISO)
    """
    if pool is None:
        logging.error("Пул соединений не инициализирован.")
        return

    # Всегда вызываем ensure_user_exists, даже если передан числовой user_id
    await ensure_user_exists(user)
    user_id = user if isinstance(user, int) else user.id

    departure = query_data.get("departure") or query_data.get("departure_city")
    arrival = query_data.get("arrival") or query_data.get("arrival_city")
    depart_date_str = query_data.get("depart_date") or query_data.get("departure_date")
    return_date_str = query_data.get("return_date")

    # Проверка обязательных полей
    if not departure or not arrival or not depart_date_str:
        logging.error("Отсутствуют обязательные поля для сохранения истории запроса.")
        return

    try:
        depart_date = date.fromisoformat(depart_date_str)
    except Exception as e:
        logging.error(f"Ошибка при преобразовании depart_date: {e}")
        return

    try:
        return_date = date.fromisoformat(return_date_str) if return_date_str else None
    except Exception as e:
        logging.error(f"Ошибка при преобразовании return_date: {e}")
        return

    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                INSERT INTO search_history(user_id, departure, arrival, departure_date, return_date)
                VALUES($1, $2, $3, $4, $5)
            """, user_id, departure, arrival, depart_date, return_date)
            logging.info("История запроса сохранена для пользователя %s.", user_id)
        except Exception as e:
            logging.error(f"Ошибка при сохранении истории запроса: {e}")

async def get_search_history(user_id: int):
    """
    Получает последние 10 запросов пользователя.
    """
    if pool is None:
        logging.error("Пул соединений не инициализирован.")
        return []
    async with pool.acquire() as connection:
        try:
            rows = await connection.fetch("""
                SELECT departure, arrival, departure_date, return_date, search_time
                FROM search_history
                WHERE user_id = $1
                ORDER BY search_time DESC
                LIMIT 10
            """, user_id)
            return rows
        except Exception as e:
            logging.error(f"Ошибка при получении истории запросов: {e}")
            return []
