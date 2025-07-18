import random
import aiosqlite
import asyncio
import datetime
from config import DATE_FORMAT
from zoneinfo import ZoneInfo

async def generate_referal():
    async with aiosqlite.connect("database.sqlite3") as db:
        cursor = await db.execute("SELECT own_referal FROM users")
        cursor = await cursor.fetchall()

        all_referals = [s[0] for s in cursor]
    

    
    alphabet = [s for s in "1234567890qwertyuiopasdfghjklzxcvbnm"]

    while True:
        referal = ""
        for i in range(8):
            referal += random.choice(alphabet)

        if referal not in all_referals:
            return referal



async def check_user(user_id, username, full_name, referal):

    async with aiosqlite.connect("database.sqlite3") as db:
        
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id, ))
        cursor = await cursor.fetchone()

        if cursor == None: # Пользователя нет в базе данных
            await db.execute("INSERT INTO USERS (user_id, username, full_name, registration_date, own_referal, from_referal, balance, stars_limit, supply_limit, gifts_amount, referal_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, username, full_name, datetime.datetime.now().strftime(DATE_FORMAT), await generate_referal(), referal, 0, "10-10000", 1000000, 0, 0))
        else:
            await db.execute("UPDATE users SET username=?, full_name=? WHERE user_id=?", (username, full_name, user_id, ))

        await db.commit()