import calendar
from aiogram import types


def generate_calendar(year: int, month: int) -> types.InlineKeyboardMarkup:
    """
    Генерирует интерактивный календарь для заданного месяца и года.
    Кнопки дат содержат callback_data вида "CALENDAR:YYYY-MM-DD",
    а кнопки навигации – "CALENDAR_NAV:prev:YYYY-MM" или "CALENDAR_NAV:next:YYYY-MM".
    """
    buttons = []

    # Заголовок с названием месяца и года
    header_text = f"{calendar.month_name[month]} {year}"
    buttons.append([types.InlineKeyboardButton(text=header_text, callback_data="IGNORE")])

    # Заголовки дней недели
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons.append([types.InlineKeyboardButton(text=day, callback_data="IGNORE") for day in weekdays])

    # Формируем календарь месяца
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(text=" ", callback_data="IGNORE"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                row.append(types.InlineKeyboardButton(text=str(day), callback_data=f"CALENDAR:{date_str}"))
        buttons.append(row)

    # Кнопки навигации для переключения месяцев
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    nav_buttons = [
        types.InlineKeyboardButton(text="<", callback_data=f"CALENDAR_NAV:prev:{prev_year}-{prev_month:02d}"),
        types.InlineKeyboardButton(text=" ", callback_data="IGNORE"),
        types.InlineKeyboardButton(text=">", callback_data=f"CALENDAR_NAV:next:{next_year}-{next_month:02d}")
    ]
    buttons.append(nav_buttons)

    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup
