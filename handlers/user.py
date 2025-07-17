from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command, CommandStart


user_router = Router()

@user_router.message(CommandStart())
async def start(message : types.Message):

    await message.answer("""
Я могу помочь тебе отслеживать появление новых подарков, автоматически скупать их и оповещать тебя.
                         
Список доступных команд:
                         
Реферальная система:
/referal - Твоя реферальная ссылка
/referalstats - Реферальная статистика
                         
Финансы:
/balance - Показать баланс
/deposit - Пополнить баланс
/refund - Вернуть звезды
                         
Уведомления:
/notifygifts - Уведомлять о новых подарках
/notifypurchase - Уведомлять о покупке новых подарков
                         
Профиль:
/profile - Общая информация
""")