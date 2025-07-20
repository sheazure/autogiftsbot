from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


async def main_menu(user_id):
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📈 Лимиты", callback_data=f"change_limits"))
    keyboard.add(InlineKeyboardButton(text="🤵‍♂️ Реферал", callback_data=f"referal_link"))
    keyboard.add(InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=f"deposit"))

    return keyboard.adjust(2).as_markup(resize_keyboard=True)


limits = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="⭐️ Звёзды"), KeyboardButton(text="📊 Саплай")], [KeyboardButton(text="↩️ Назад")]], resize_keyboard=True)

cancel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✖️ Отменить", callback_data="cancel")]])

reply_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✖️ Отменить")]], resize_keyboard=True)


async def answer(user_id, message_id):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Ответить", callback_data=f"answer:{user_id}:{message_id}")]], resize_keyboard=True)

    return keyboard