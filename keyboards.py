from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import aiosqlite


main_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 Лимиты", callback_data=f"change_limits"), InlineKeyboardButton(text="🤵‍♂️ Реферал", callback_data=f"referal_link")],
                                                  [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=f"deposit")],
                                                  [InlineKeyboardButton(text="🗣 Подключить канал", callback_data="connect_channel")]])


async def main_menu(user_id):

    async with aiosqlite.connect('database.sqlite3') as db:
        info = await db.execute("SELECT connected_channel FROM users WHERE user_id=?", (user_id, ))
        info = await info.fetchone()
        info = info[0]

        if info == None: # Канала нет
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 Лимиты", callback_data=f"change_limits"), InlineKeyboardButton(text="🤵‍♂️ Реферал", callback_data=f"referal_link")],
                                                  [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=f"deposit")],
                                                  [InlineKeyboardButton(text="🗣 Подключить канал", callback_data="connect_channel")]])
        else:
            return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📈 Лимиты", callback_data=f"change_limits"), InlineKeyboardButton(text="🤵‍♂️ Реферал", callback_data=f"referal_link")],
                                                  [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=f"deposit")],
                                                  [InlineKeyboardButton(text="🗣 Отключить канал", callback_data="disconnect_channel")]])

limits = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⭐️ Звёзды", callback_data="change_stars_limit"), InlineKeyboardButton(text="📊 Саплай", callback_data="change_supply_limit")],
                                               [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main_menu")]])

cancel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✖️ Отменить", callback_data="cancel")]])

reply_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✖️ Отменить")]], resize_keyboard=True)


async def answer(user_id, message_id):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Ответить", callback_data=f"answer:{user_id}:{message_id}")]], resize_keyboard=True)

    return keyboard


back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main_menu")]])