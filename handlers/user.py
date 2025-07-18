from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandStart
from utils import check_user
import aiosqlite
from config import DB_PATH

user_router = Router()

@user_router.message(CommandStart())
async def start(message : types.Message):
    if len(message.text.split()) == 1: # Рефа нет
        referal = None
    else:
        referal = message.text.split()[1]

    await check_user(message.from_user.id, message.from_user.username, message.from_user.full_name, referal)

    await message.answer("""
Я могу помочь тебе отслеживать появление новых подарков, автоматически скупать их и оповещать тебя.
                         
<b>Список доступных команд:</b>
                         
<b>Финансы:</b>
/balance - Показать баланс
/deposit - Пополнить баланс
/refund - Вернуть звезды
                         
<b>Уведомления:</b>
/notifygifts - Уведомлять о новых подарках
/notifypurchase - Уведомлять о покупке новых подарков
                         
<b>Профиль:</b>
/profile - Общая информация
/stats - Общая статистика
                                                  
<b>Реферальная система:</b>
/referal - Твоя реферальная ссылка

                                            
<i>Если у вас есть вопросы, вы всегда можете обратиться в поддержку - @потом на новую симку ворк акк создам</i>
""", parse_mode="HTML")
    

@user_router.message(Command("referal"))
async def referal(message : types.Message):

    async with aiosqlite.connect(DB_PATH) as db:
        own_referal = await db.execute("SELECT own_referal FROM users WHERE user_id=?", (message.from_user.id, ))
        own_referal = await own_referal.fetchone()
        own_referal = own_referal[0]
    text = f"<b>Твоя реферальная ссылка</b>\n\n👉 https://t.me/giftshaunterbot/?start={own_referal}\n\nПоделись ею со своими друзьями и начни получать 5% от их депозита на свой счет 💸"

    await message.answer(text, parse_mode="HTML")



@user_router.message(Command("menu"))
async def menu(message : types.Message):
    
    async with aiosqlite.connect(DB_PATH) as db:

        info = await db.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id, ))
        info = await info.fetchone()

    text = f"<b>Главное меню</b>\n\n<b>Ваш баланс:</b> {info[6]} ⭐️\n\n<b>Статистика:</b>\nКоличество приглашенных пользователей: ???\nКоличество купленных подарков: ???\n\n<b>Ваши лимиты:</b>\nЗвезды:\nСаплай:\n\n<i>Если у вас есть вопросы, вы всегда можете обратиться в поддержку - /help</i>"

    await message.answer(text, parse_mode="HTML")