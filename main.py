import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db, get_tasks_to_notify, set_task_notified
from handlers import start, menu, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime

async def send_reminders(bot: Bot):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tasks_to_notify = await get_tasks_to_notify(now)
    for task_id, user_id, text in tasks_to_notify:
        try:
            await bot.send_message(user_id, f"⏰ Напоминание о задаче:\n{text}")
            await set_task_notified(task_id)
        except Exception as e:
            print(f"Ошибка при отправке напоминания: {e}")

async def main():
    await init_db()
    bot = Bot(token=BOT_TOKEN) # bot token in .env
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(tasks.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_reminders, 'interval', minutes=1, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
