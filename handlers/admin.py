from aiogram import Router, Bot, F, types
from aiogram.filters import Command
import keyboards
from utils import check_admin
import aiosqlite


admin_router = Router()


@admin_router.message(Command("show_users"))
async def show_users(message : types.Message):

    if not await check_admin(message.from_user.id):
        return
    
    async with aiosqlite.connect('database.sqlite3') as db:
        info = await db.execute("SELECT username, full_name, registration_date, balance FROM users")
        users = await info.fetchall()

        text = ""
        for user in users:
            text += f"Полное имя: {user[1]}\nЮзернейм: {user[0]}\nДата регистрации: {user[2]}\nБаланс: {user[3]}\n\n"

    await message.answer(text=text)


@admin_router.message(Command("add_admin"))
async def add_admin(message : types.Message, bot : Bot):

    if message.from_user.id != 1404205394:
        return
    
    if len(message.text.split()) == 1:
        await message.answer("/add_admin @username")
        return
    
    async with aiosqlite.connect('database.sqlite3') as db:
        info = await db.execute("SELECT user_id, full_name FROM users WHERE username=?", (message.text.split()[1], ))
        info = await info.fetchone()

        if info == None:
            await message.answer("Пользователя нет в нашей базе данных!")
            return
        user_id = info[0]
        full_name = info[1]

        await db.execute("INSERT INTO admins (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, message.text.split()[1], full_name, ))
        await db.commit()

        await message.answer(f"Вы успешно добавили нового админа {full_name} ({message.text.split()[1]})")
