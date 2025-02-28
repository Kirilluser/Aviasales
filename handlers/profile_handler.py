from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

router = Router()


# Создаем состояния для FSM
class ProfileState(StatesGroup):
    country = State()
    phone = State()

# Хранилище профилей пользователей (можно заменить на БД)
user_profiles = {}


# Команда /profile
@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    profile = user_profiles.get(user_id, {})
    country = profile.get("country", "Не указана")
    phone = profile.get("phone", "Не указан")

    response = (f"\U0001F464 <b>Ваш профиль:</b>\n"
                f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                f"👤 <b>Имя:</b> {message.from_user.full_name}\n"
                f"📛 <b>Юзернейм:</b> @{message.from_user.username if message.from_user.username else 'не указан'}\n"
                f"🌍 <b>Язык:</b> {message.from_user.language_code if message.from_user.language_code else 'не указан'}\n"
                f"🌍 <b>Страна:</b> {country}\n"
                f"📞 <b>Телефон:</b> {phone}\n\n"
                "Вы можете обновить данные, выбрав одну из опций ниже:")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Изменить страну", callback_data="profile:country")],
        [types.InlineKeyboardButton(text="Изменить телефон", callback_data="profile:phone")]
    ])

    photos = await message.bot.get_user_profile_photos(user_id)
    if photos.total_count > 0:
        photo = photos.photos[0][-1]
        await message.answer_photo(photo=photo.file_id, caption=response, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(response, parse_mode="HTML", reply_markup=keyboard)


# Обработчик нажатия "Изменить страну"
@router.callback_query(lambda c: c.data == "profile:country")
async def change_country(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileState.country)
    await callback.message.answer("🌍 Введите вашу страну:")
    await callback.answer()


# Обработчик ввода страны
@router.message(ProfileState.country)
async def process_country(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profiles.setdefault(user_id, {})["country"] = message.text.strip()
    await state.clear()
    await message.answer("✅ Страна успешно обновлена! Используйте /profile для просмотра данных.")


# Обработчик нажатия "Изменить телефон"
@router.callback_query(lambda c: c.data == "profile:phone")
async def change_phone(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileState.phone)
    await callback.message.answer("📞 Введите ваш номер телефона (в формате +1234567890):")
    await callback.answer()


# Обработчик ввода телефона
@router.message(ProfileState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_profiles.setdefault(user_id, {})["phone"] = message.text.strip()
    await state.clear()
    await message.answer("✅ Номер телефона успешно обновлен! Используйте /profile для просмотра данных.")
