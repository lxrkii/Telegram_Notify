from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from db import get_tasks, complete_task, delete_task

router = Router()

@router.message(F.text == "📋 Список задач")
async def show_tasks(message: types.Message):
    if not message.from_user:
        await message.answer("Ошибка: не удалось определить пользователя.")
        return
    tasks = await get_tasks(message.from_user.id, status="active")
    if not tasks:
        await message.answer("У вас нет активных задач.")
        return
    for task in tasks:
        if len(task) == 5:
            task_id, text, due_date, is_done, category = task
        else:
            task_id, text, due_date, is_done = task
            category = "Без категории"
        buttons = [
            [
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"complete_{task_id}"),
                InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
            ]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(f"📝 <b>{text}</b>\n⏰ {due_date}\n🏷 Категория: {category}", reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data.startswith("complete_"))
async def complete_task_callback(call: CallbackQuery):
    if call.data:
        task_id = int(call.data.split("_")[1])
    await complete_task(task_id)
    await call.answer("Задача завершена!", show_alert=True)
    if isinstance(call.message, Message):
        await call.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("delete_"))
async def delete_task_callback(call: CallbackQuery):
    if call.data:
        task_id = int(call.data.split("_")[1])
    await delete_task(task_id)
    await call.answer("Задача удалена!", show_alert=True)
    if isinstance(call.message, Message):
        await call.message.edit_reply_markup(reply_markup=None) 