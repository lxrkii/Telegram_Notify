from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import add_task
import datetime

router = Router()

# Основное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Добавить задачу")],
        [KeyboardButton(text="📋 Список задач")],
        [KeyboardButton(text="⏰ Напоминания"), KeyboardButton(text="⚙️ Настройки")]
    ],
    resize_keyboard=True
)

CATEGORIES = ["Работа", "Личное", "Учёба", "Другое"]

@router.message(F.text == "Начать")
async def show_main_menu(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

# FSM для добавления задачи
class AddTask(StatesGroup):
    waiting_for_text = State()
    waiting_for_due_date = State()
    waiting_for_reminder = State()
    waiting_for_remind_at = State()
    waiting_for_category = State()

@router.message(F.text == "📝 Добавить задачу")
async def add_task_start(message: types.Message, state: FSMContext):
    await message.answer("Введите текст задачи:")
    await state.set_state(AddTask.waiting_for_text)

@router.message(AddTask.waiting_for_text)
async def add_task_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Когда нужно выполнить задачу? (формат: ГГГГ-ММ-ДД ЧЧ:ММ)")
    await state.set_state(AddTask.waiting_for_due_date)

@router.message(AddTask.waiting_for_due_date)
async def add_task_due_date(message: types.Message, state: FSMContext):
    try:
        due_date = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Некорректный формат даты. Попробуйте ещё раз (ГГГГ-ММ-ДД ЧЧ:ММ):")
        return
    await state.update_data(due_date=due_date.strftime("%Y-%m-%d %H:%M"))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]],
        resize_keyboard=True
    )
    await message.answer("Установить напоминание? (Да/Нет)", reply_markup=keyboard)
    await state.set_state(AddTask.waiting_for_reminder)

@router.message(AddTask.waiting_for_reminder)
async def add_task_reminder(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        await message.answer("Когда напомнить? (формат: ГГГГ-ММ-ДД ЧЧ:ММ)")
        await state.set_state(AddTask.waiting_for_remind_at)
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cat)] for cat in CATEGORIES],
            resize_keyboard=True
        )
        await message.answer("Выберите категорию задачи:", reply_markup=keyboard)
        await state.set_state(AddTask.waiting_for_category)

@router.message(AddTask.waiting_for_remind_at)
async def add_task_remind_at(message: types.Message, state: FSMContext):
    try:
        remind_at = datetime.datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Некорректный формат даты. Попробуйте ещё раз (ГГГГ-ММ-ДД ЧЧ:ММ):")
        return
    await state.update_data(remind_at=remind_at.strftime("%Y-%m-%d %H:%M"))
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in CATEGORIES],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию задачи:", reply_markup=keyboard)
    await state.set_state(AddTask.waiting_for_category)

@router.message(AddTask.waiting_for_category)
async def add_task_category(message: types.Message, state: FSMContext):
    category = message.text if message.text in CATEGORIES else "Другое"
    data = await state.get_data()
    await add_task(
        user_id=message.from_user.id,
        text=data["text"],
        due_date=data["due_date"],
        remind_at=data.get("remind_at"),
        category=category
    )
    await message.answer("Задача с категорией добавлена!", reply_markup=main_menu)
    await state.clear() 