import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from handlers.user import user_router
from handlers.admin import admin_router
from utils import check_new_gifts

bot = Bot(token='8161292063:AAHFKVjPOHicfsCUK3BHLlUo5TIHw48qppQ')
dp = Dispatcher()


async def create_database():
    async with aiosqlite.connect("database.sqlite3") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS users (
                         user_id INTEGER,
                         username TEXT, 
                         full_name TEXT, 
                         registration_date TEXT, 
                         own_referal TEXT, 
                         from_referal TEXT, 
                         balance INTEGER,
                         stars_limit TEXT,
                         supply_limit INTEGER,
                         gifts_amount INTEGER,
                         referal_amount INTEGER
                         )""")
        
        await db.execute("""CREATE TABLE IF NOT EXISTS admins (
                         user_id INTEGER,
                         username TEXT,
                         full_name)""")
        
        await db.commit()


async def main():
    asyncio.create_task(check_new_gifts(bot))
    await create_database()
    dp.include_routers(user_router, admin_router)
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())

