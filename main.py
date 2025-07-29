import asyncio
import aiosqlite
import logging
from aiogram import Bot, Dispatcher
from handlers.user import user_router
from handlers.admin import admin_router
from utils import check_new_gifts



bot = Bot(token='8161292063:AAHFKVjPOHicfsCUK3BHLlUo5TIHw48qppQ')
dp = Dispatcher()


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__(level=logging.WARNING)
        self.bot = bot
        self.chat_id = chat_id

    async def emit_async(self, record):
        log_entry = self.format(record)
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=f"📢 {log_entry}")
        except Exception as e:
            print(f"Ошибка при отправке лога: {e}")

    def emit(self, record):

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.emit_async(record))
        except RuntimeError:    
            pass

logger = logging.getLogger("mybot")
logger.setLevel(logging.WARNING)

tg_handler = TelegramLogHandler(bot, 1404205394)
tg_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(tg_handler)



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
                         referal_amount INTEGER,
                         connected_channel TEXT
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

