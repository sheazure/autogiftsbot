import random
import aiosqlite
import asyncio
import datetime
from config import DATE_FORMAT
from zoneinfo import ZoneInfo
from aiogram.methods.get_available_gifts import GetAvailableGifts
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError


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
            if referal != None:
                await db.execute("UPDATE users SET referal_amount=referal_amount+1 WHERE own_referal=?", (referal, ))
        else:
            await db.execute("UPDATE users SET username=?, full_name=? WHERE user_id=?", (username, full_name, user_id, ))

        await db.commit()



async def check_new_gifts(bot : Bot):
    while True:
        print(f"Checking new gifts {datetime.datetime.now().strftime(DATE_FORMAT)}")
        try:
            gifts = await bot(GetAvailableGifts())
        except:
            await bot.send_message(1404205394, "ОШИБКА ПОЛУЧЕНИЯ НОВЫХ ПОДАРКОВ!!!")

        gifts_list = []
        for gift in gifts:
            for item in gift[1]:
                d = {}
                for it in item:
                    if it[0] == "sticker":
                        continue
                    d[it[0]] = it[1]
                gifts_list.append(d)

        rare_gifts = []

        for gift in gifts_list:
            if gift["total_count"] != None: # Лимитированный подарок
                rare_gifts.append(gift)

        rare_gifts = sorted(rare_gifts, key=lambda x:x["total_count"])
        
        if len(rare_gifts) != 0:
            print(f"NEW GIFTS, AMOUNT: {len(rare_gifts)}")
            await bot.send_message(1404205394, "НОВЫЕ ПОДАРКИ!!!")
            await buy_rare_gifts(rare_gifts, bot)
        else:
            print("No gifts...")

        await asyncio.sleep(5)


async def buy_rare_gifts(rare_gifts : list, bot : Bot):


    while True:
        async with aiosqlite.connect('database.sqlite3') as db:
            for gift in rare_gifts:
                users = await db.execute("SELECT * FROM users")
                users = await users.fetchall()
                bought_gifts = 0
                for user in users:
                    balance = user[6]
                    down_stars_limit = user[7].split("-")[0]
                    up_stars_limit = user[7].split('-')[1]
                    supply_limit = user[8]

                    if balance >= gift["star_count"] and down_stars_limit <= gift["star_count"] <= up_stars_limit and gift["total_count"] <= supply_limit:
                        try:
                            await bot.send_gift(gift_id=gift["id"], user_id=user[0])
                        except TelegramAPIError as e:
                            print(f"Ошибка покупки {e}")
                            pass
                        else:
                            bought_gifts += 1
                            await db.execute("UPDATE users SET balance=balance-? gifts_amount=gifts_amount+1 WHERE user_id=?", (gift["star_count"], user[0]))

                if bought_gifts == 0: # Не куплено ни одного подарка
                    rare_gifts.remove(gift)
