import aiosqlite
import datetime
from typing import Optional

DB_NAME = 'bot.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                due_date DATETIME NOT NULL,
                remind_at DATETIME,
                is_done BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        await db.commit()

async def add_user(user_id: int, name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (id, name, created_at) VALUES (?, ?, ?)',
            (user_id, name, datetime.datetime.now())
        )
        await db.commit()

async def add_task(user_id: int, text: str, due_date: str, remind_at: Optional[str] = None, category: str = 'Без категории'):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO tasks (user_id, text, due_date, remind_at, is_done, created_at, category) VALUES (?, ?, ?, ?, 0, ?, ?)',
            (user_id, text, due_date, remind_at, datetime.datetime.now(), category)
        )
        await db.commit()

async def get_tasks(user_id: int, status: str = "all"):
    query = "SELECT id, text, due_date, is_done FROM tasks WHERE user_id = ?"
    params = [user_id]
    if status == "active":
        query += " AND is_done = 0"
    elif status == "done":
        query += " AND is_done = 1"
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def complete_task(task_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE tasks SET is_done = 1 WHERE id = ?", (task_id,))
        await db.commit()

async def delete_task(task_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await db.commit()

async def migrate_add_notified():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            ALTER TABLE tasks ADD COLUMN notified BOOLEAN NOT NULL DEFAULT 0
        ''')
        await db.commit()

async def migrate_add_category():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'Без категории'
        ''')
        await db.commit()

async def get_tasks_to_notify(now: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT id, user_id, text FROM tasks WHERE remind_at IS NOT NULL AND remind_at <= ? AND is_done = 0 AND notified = 0',
            (now,)
        ) as cursor:
            return await cursor.fetchall()

async def set_task_notified(task_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE tasks SET notified = 1 WHERE id = ?', (task_id,))
        await db.commit()
