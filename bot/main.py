import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dotenv import load_dotenv
import asyncpg

# ========================
# Настройка логирования
# ========================
logging.basicConfig(level=logging.INFO)

# ========================
# Загружаем .env
# ========================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = os.getenv("ADMINS", "").split(",")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# ========================
# Бот и диспетчер
# ========================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())


# ========================
# Подключение к БД
# ========================
async def create_db():
    conn = await asyncpg.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT UNIQUE,
            username TEXT,
            role INT DEFAULT 0
        );
        """
    )
    await conn.close()


# ========================
# Роли
# ========================
ROLES = {
    0: "Клиент",
    1: "Работник",
    2: "Админ",
    3: "Владелец"
}


# ========================
# Команды
# ========================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Это магазин-бот.\nИспользуй /whoami чтобы узнать свою роль.")


@dp.message(Command("whoami"))
async def cmd_whoami(message: Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "Без ника"
    if username in ADMINS:
        role = 3
    else:
        role = 0
    await message.answer(f"👤 Ваш профиль:\nID: <code>{user_id}</code>\nНик: @{username}\nРоль: {ROLES.get(role)}")


# ========================
# Запуск
# ========================
async def main():
    await create_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
