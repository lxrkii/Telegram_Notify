from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import add_user

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    if user is None:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return
    name = user.full_name or user.username or "Пользователь"
    await add_user(user.id, name)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Начать")]],
        resize_keyboard=True
    )
    text = (
        f"👋 Привет, {name}!\n\n"
        "Я — твой помощник для планирования задач.\n"
        "Создавай задачи, получай напоминания и управляй своим временем прямо в Telegram!"
    )
    await message.answer(text, reply_markup=keyboard) 