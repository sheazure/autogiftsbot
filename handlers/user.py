from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import check_user, back_to_main_menu
import aiosqlite
import keyboards
import os
import math
from logger import logger
user_router = Router()


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.sqlite3")

@user_router.message(CommandStart())
async def start(message : types.Message):
    
    if len(message.text.split()) == 1: # Рефа нет
        referal = None
    else:
        referal = message.text.split()[1]

    logger.info(f"/start from {message.from_user.full_name} (@{message.from_user.username}). Referal - {referal}")

    await check_user(message.from_user.id, message.from_user.username, message.from_user.full_name, referal)
    await menu(message)
    

@user_router.message(Command("referal"))
async def referal(message : types.Message):
    logger.info(f"/referal from {message.from_user.full_name} (@{message.from_user.username})")
    async with aiosqlite.connect(DB_PATH) as db:
        own_referal = await db.execute("SELECT own_referal FROM users WHERE user_id=?", (message.from_user.id, ))
        own_referal = await own_referal.fetchone()
        own_referal = own_referal[0]
    text = f"👥 <b>Твоя реферальная ссылка</b>\n\n👉 https://t.me/giftshaunterbot/?start={own_referal}\n\nПоделись ей со своими друзьями и начни получать 5% от их депозита на свой счет 💸"

    await message.answer(text, parse_mode="HTML")



@user_router.message(Command("menu"))
async def menu(message : types.Message):
    await check_user(message.from_user.id, message.from_user.username, message.from_user.full_name, None)
    logger.info(f"/menu from {message.from_user.full_name} (@{message.from_user.username})")
    async with aiosqlite.connect(DB_PATH) as db:

        info = await db.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id, ))
        info = await info.fetchone()

    text = f"🏠 <b>Главное меню</b>\n\n<b>Ваш баланс: {info[6]}</b> ⭐️\n\n📊 <b>Статистика:</b>\nКоличество приглашенных пользователей: <b>{info[10]}</b> 👤\nКоличество купленных подарков: <b>{info[9]}</b> 🎁\n\n📈 <b>Ваши лимиты:</b>\n⭐️ Звезды: от <b>{info[7].split('-')[0]}</b> до <b>{info[7].split('-')[1]}</b>\n🎁 Саплай: до <b>{info[8]}</b>\n\n🗣 <b>Подключенный канал:</b> {(info[11] if info[11] != None else "Нет")}\n\n<i>Если у вас есть вопросы, вы всегда можете обратиться в поддержку - /help</i>"

    await message.answer(text, parse_mode="HTML", reply_markup=await keyboards.main_menu(message.from_user.id))



class ChangeLimits(StatesGroup):
    step1 = State()

class Answer(StatesGroup):
    step = State()

class Deposit(StatesGroup):
    step = State()

class ConnectChannel(StatesGroup):
    step = State()

class ChangeStarsLimit(StatesGroup):
    step = State()

class ChangeSupplyLimit(StatesGroup):
    step = State()

@user_router.callback_query()
async def callback_query(callback : types.CallbackQuery, state : FSMContext, bot : Bot):

    await callback.answer("")

    if callback.data == "cancel":
        await callback.message.delete()
        await state.clear()

    if callback.data == "change_limits":
        await callback.message.edit_text(text="Какие лимиты вы хотите изменить?", reply_markup=keyboards.limits)


    if callback.data.split(":")[0] == "answer":
        to_edit = await callback.message.answer(f"Напишите ответ пользователю {callback.message.text[19:callback.message.text.find(" (")]}", reply_markup=keyboards.cancel)
        await state.set_state(Answer.step)
        await state.update_data(chat_id=callback.data.split(":")[1])
        await state.update_data(message_id=callback.data.split(":")[2])
        await state.update_data(to_edit=to_edit.message_id)
        await state.update_data(to_edit2=callback.message.message_id)
        await state.update_data(previous_text=callback.message.text)

    if callback.data == "referal_link":
        logger.info(f"/referal from {callback.from_user.full_name} (@{callback.from_user.username})")
        async with aiosqlite.connect(DB_PATH) as db:
            own_referal = await db.execute("SELECT own_referal FROM users WHERE user_id=?", (callback.from_user.id, ))
            own_referal = await own_referal.fetchone()
            own_referal = own_referal[0]
        text = f"👥 <b>Твоя реферальная ссылка</b>\n\n👉 https://t.me/giftshaunterbot/?start={own_referal}\n\nПоделись ею со своими друзьями и начни получать 5% от их депозита на свой счет 💸"

        await callback.message.answer(text, parse_mode="HTML")

    if callback.data == "deposit":
        to_edit = await callback.message.answer("⭐️ Введите количество звёзд, которое вы хотите отправить боту.", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
        await state.set_state(Deposit.step)



    if callback.data == "connect_channel":
        to_edit = await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Чтобы подключить телеграм канал, отправьте его юзернейм в формате @durov\n\n<i>*Подарки будут отправляться в телеграм канал</i>", parse_mode="HTML", reply_markup=keyboards.back_to_main_menu)
        await state.set_state(ConnectChannel.step)
        await state.update_data(to_edit=to_edit.message_id)

    if callback.data == "disconnect_channel":
        
        async with aiosqlite.connect('database.sqlite3') as db:
            await db.execute("UPDATE users SET connected_channel=NULL WHERE user_id=?", (callback.message.chat.id, ))
            await db.commit()
        await callback.message.answer("🗣 Вы успешно отключили Телеграм канал!")

        await back_to_main_menu(callback.message.chat.id, callback.message.message_id, bot)

    if callback.data == "back_to_main_menu":
        await state.clear()
        await back_to_main_menu(callback.message.chat.id, callback.message.message_id, bot)


    if callback.data == "change_stars_limit":
        to_edit = await callback.message.edit_text("⭐️ Введите лимит на цену подарков в формате <b>10-10000</b>.\n<i>Пример - <b>100-2000</b></i>", parse_mode="HTML")
        await callback.message.edit_reply_markup(reply_markup=keyboards.back_to_main_menu)

        await state.update_data(to_edit=to_edit.message_id)
        await state.set_state(ChangeStarsLimit.step)

    if callback.data == "change_supply_limit":
        to_edit = await callback.message.edit_text("🎁 Введите лимит на саплай Телеграм подарков.\n<i>Лимит должен быть числом)</i>", parse_mode="HTML")
        await callback.message.edit_reply_markup(reply_markup=keyboards.back_to_main_menu)

        await state.update_data(to_edit=to_edit.message_id)
        await state.set_state(ChangeSupplyLimit.step)

class Help(StatesGroup):
    step = State()


@user_router.message(Command("help"))
async def help(message : types.Message, state : FSMContext):

    to_edit = await message.answer("💬 Здесь вы можете написать свое <b>обращение</b> нашим модераторам.\n\n<i>Ожидание ответа может составлять до 12 часов.</i>", parse_mode="HTML", reply_markup=keyboards.cancel)
    await state.set_state(Help.step)
    await state.update_data(to_edit=to_edit.message_id)

@user_router.message(Help.step)
async def help2(message : types.Message, state : FSMContext, bot : Bot):

    temp = await state.get_data()
    to_edit = temp["to_edit"]
    await bot.edit_message_reply_markup(chat_id = message.chat.id, message_id=to_edit, reply_markup=None)

    await bot.send_message(chat_id=1404205394, text=f"Новое обращение от {message.from_user.full_name} (@{message.from_user.username})\n\n{message.text}", reply_markup=await keyboards.answer(message.from_user.id, message.message_id))
    
    await message.reply("📩 Ваше сообщение было отправлено модераторам, ожидайте ответа!")



@user_router.message(Answer.step)
async def answer(message : types.Message, state : FSMContext, bot : Bot):

    text = message.text
    temp = await state.get_data()
    to_edit = temp["to_edit"]
    to_edit2 = temp["to_edit2"]
    chat_id = temp["chat_id"]
    message_id = temp["message_id"]
    previous_text = temp["previous_text"]


    text = "📩 <b>Вам пришел ответ от модерации!</b>\n\n" + text

    await bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=message_id, parse_mode="HTML")

    await bot.edit_message_text(chat_id=message.chat.id, message_id=to_edit2, text=previous_text+f"\n\n✅ <b>Ваш ответ:</b> <i>{message.text}</i>", parse_mode="HTML")
    await message.delete()
    await bot.delete_message(chat_id=message.chat.id, message_id=to_edit)




@user_router.message(F.text, Deposit.step)
async def deposit(message : types.Message, state : FSMContext, bot : Bot):
    data = await state.get_data()
    to_edit = data["to_edit"]

    try:
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=to_edit, reply_markup=None)
    except:
        pass

    if not message.text.isdigit():
        to_edit = await message.answer("❌ Количество звёзд должно быть числом!", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
        return
    
    amount = int(message.text)

    await message.answer(f"Комиссия данного платежа составит <b>10% ({int(amount * 0.1)}</b> ⭐️)\n\n<i>5% - вашему рефералу, 5% - на тех.обслуживание бота.</i>", parse_mode="HTML")
    await bot.send_invoice(chat_id=message.chat.id,
                           title="Депозит",
                           description=f"Пополнение баланса на {message.text} звёзд.",
                           currency="XTR",
                           prices=[types.LabeledPrice(label=f"{message.text} ⭐️", amount=amount)],
                           payload=f"deposit:{message.from_user.id}:{amount}"
                           )
    

    

@user_router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q : types.PreCheckoutQuery, bot : Bot):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@user_router.message(F.successful_payment)
async def successful_payment(message : types.Message, bot : Bot):
    payment_info = message.successful_payment
    
    amount = int(payment_info.invoice_payload.split(':')[2])
    user_id = int(payment_info.invoice_payload.split(":")[1])

    logger.info(f"SUCCESSFUL PAYMENT FROM {message.from_user.full_name} (@{message.from_user.username}). AMOUNT: {amount}")

    async with aiosqlite.connect(DB_PATH) as db:
        referal = await db.execute("SELECT from_referal FROM users WHERE user_id=?", (message.from_user.id, ))
        referal = await referal.fetchone()
        referal = referal[0]

        if referal == None: # Реферала нет
            referal_user_id = None
        else: # Реферал есть
            referal_user_id = await db.execute("SELECT user_id FROM users WHERE own_referal=?", (referal, ))
            referal_user_id = await referal_user_id.fetchone()
            referal_user_id = referal_user_id[0]

        for_user = math.ceil(amount * 0.9)
        
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (for_user, message.from_user.id, ))
        await bot.send_message(user_id, f"Вы успешно пополнили баланс на <b>{for_user}</b> ⭐️! Ваша комиссия составила 10%.\n\n/menu - Главное меню", parse_mode="HTML")
        
        for_admins = amount - for_user

        if referal_user_id != None:
            for_admins = (amount - for_user) // 2
            balance = await db.execute("SELECT balance FROM users WHERE user_id=?", (referal_user_id, ))
            balance = await balance.fetchone()
            balance = balance[0]


            await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount - for_user - for_admins), referal_user_id, )
            await bot.send_message(referal_user_id, f"Один из ваших друзей воспользовался вашей реферальной ссылкой и вы получили % от его депозита.\n\nВаш баланс: <strike>{balance}</strike> {balance + int(amount * 0.05)}", parse_mode="HTML")

        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (for_admins, 1404205394, ))

        await db.commit()




@user_router.message(ConnectChannel.step)
async def connect_channel(message : types.Message, state : FSMContext, bot : Bot):

    data = await state.get_data()

    to_edit = data["to_edit"]
    
    channel = (message.text if message.text[0] == "@" else "@"+message.text)

    async with aiosqlite.connect('database.sqlite3') as db:
        await db.execute("UPDATE users SET connected_channel=? WHERE user_id=?", (channel, message.from_user.id, ))
        await db.commit()
    
    
    await message.answer("🗣 Вы успешно подключили свой телеграм канал!")
    logger.info(f"{message.from_user.full_name} (@{message.from_user.username}) подключил канал {channel}")

    await back_to_main_menu(message.chat.id, message_id=to_edit, bot=bot)
    await state.clear()



@user_router.message(ChangeStarsLimit.step)
async def change_stars_limit(message : types.Message, state : FSMContext, bot : Bot):

    # Неверный формат
    if not message.text.split("-")[0].isdigit() or not message.text.split("-")[1].isdigit() or "-" not in message.text:
        await message.delete()
        return
    
    async with aiosqlite.connect('database.sqlite3') as db:
        await db.execute("UPDATE users SET stars_limit=? WHERE user_id=?", (message.text, message.from_user.id, ))
        await db.commit()
    
    await message.answer("📈 Вы успешно обновили лимиты на цены подарков!")

    data = await state.get_data()
    to_edit = data["to_edit"]

    await back_to_main_menu(chat_id=message.chat.id, message_id=to_edit, bot=bot)
    await state.clear()


@user_router.message(ChangeSupplyLimit.step)
async def change_supply_limit(message : types.Message, state : FSMContext, bot : Bot):

    # Неверный формат
    if not message.text.isdigit():
        await message.delete()
        return
    
    async with aiosqlite.connect("database.sqlite3") as db:
        await db.execute("UPDATE users SET supply_limit=? WHERE user_id=?", (int(message.text), message.from_user.id, ))
        await db.commit()

    await message.answer("🎁 Вы успешно обновили лимит на саплай подарков!")

    data = await state.get_data()
    to_edit = data["to_edit"]

    await back_to_main_menu(chat_id=message.chat.id, message_id=to_edit, bot=bot)
    await state.clear()

