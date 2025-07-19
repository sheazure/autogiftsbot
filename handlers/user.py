from aiogram import Router, F, Bot
from aiogram import types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils import check_user
import aiosqlite
from config import DB_PATH
import keyboards
from config import PROVIDER_TOKEN
from aiogram.methods.get_available_gifts import GetAvailableGifts

user_router = Router()

@user_router.message(CommandStart())
async def start(message : types.Message):
    if len(message.text.split()) == 1: # Рефа нет
        referal = None
    else:
        referal = message.text.split()[1]

    await check_user(message.from_user.id, message.from_user.username, message.from_user.full_name, referal)
    await menu(message)
    

@user_router.message(Command("referal"))
async def referal(message : types.Message):

    async with aiosqlite.connect(DB_PATH) as db:
        own_referal = await db.execute("SELECT own_referal FROM users WHERE user_id=?", (message.from_user.id, ))
        own_referal = await own_referal.fetchone()
        own_referal = own_referal[0]
    text = f"👥 <b>Твоя реферальная ссылка</b>\n\n👉 https://t.me/giftshaunterbot/?start={own_referal}\n\nПоделись ею со своими друзьями и начни получать 5% от их депозита на свой счет 💸"

    await message.answer(text, parse_mode="HTML")



@user_router.message(Command("menu"))
async def menu(message : types.Message):
    
    async with aiosqlite.connect(DB_PATH) as db:

        info = await db.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id, ))
        info = await info.fetchone()

    text = f"🏠 <b>Главное меню</b>\n\n<b>Ваш баланс: {info[6]}</b> ⭐️\n\n📊 <b>Статистика:</b>\nКоличество приглашенных пользователей: <b>{info[10]}</b> 👤\nКоличество купленных подарков: <b>{info[9]}</b> 🎁\n\n📈 <b>Ваши лимиты:</b>\n⭐️ Звезды: от <b>{info[7].split('-')[0]}</b> до <b>{info[7].split('-')[1]}</b>\n🎁 Саплай: до <b>{info[8]}</b>\n\n<i>Если у вас есть вопросы, вы всегда можете обратиться в поддержку - /help</i>"

    await message.answer(text, parse_mode="HTML", reply_markup=await keyboards.main_menu(message.from_user.id))



class ChangeLimits(StatesGroup):
    step1 = State()


class Answer(StatesGroup):
    step = State()



class Deposit(StatesGroup):
    step = State()

@user_router.callback_query()
async def callback_query(callback : types.CallbackQuery, state : FSMContext, bot : Bot):

    await callback.answer("")

    if callback.data == "cancel":
        await callback.message.delete()
        await state.clear()

    if callback.data == "change_limits":
        await callback.message.answer("Какие лимиты вы хотите изменить?", reply_markup=keyboards.limits)
        await state.update_data(to_del_keyboard=callback.message)
        await state.set_state(ChangeLimits.step1)


    if callback.data.split(":")[0] == "answer":
        to_edit = await callback.message.answer(f"Напишите ответ пользователю {callback.message.text[19:callback.message.text.find(" (")]}", reply_markup=keyboards.cancel)
        await state.set_state(Answer.step)
        await state.update_data(chat_id=callback.data.split(":")[1])
        await state.update_data(message_id=callback.data.split(":")[2])
        await state.update_data(to_edit=to_edit.message_id)
        await state.update_data(to_edit2=callback.message.message_id)
        await state.update_data(previous_text=callback.message.text)

    if callback.data == "referal_link":
        async with aiosqlite.connect(DB_PATH) as db:
            own_referal = await db.execute("SELECT own_referal FROM users WHERE user_id=?", (callback.from_user.id, ))
            own_referal = await own_referal.fetchone()
            own_referal = own_referal[0]
        text = f"👥 <b>Твоя реферальная ссылка</b>\n\n👉 https://t.me/giftshaunterbot/?start={own_referal}\n\nПоделись ею со своими друзьями и начни получать 5% от их депозита на свой счет 💸"

        await callback.message.answer(text, parse_mode="HTML")

    if callback.data == "deposit":
        to_edit = await callback.message.answer("Введите количество звёзд, которое вы хотите отправить боту.", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
        await state.set_state(Deposit.step)


class ChangeStarLimits(StatesGroup):
    step1 = State()
    step2 = State()

class ChangeSupplyLimits(StatesGroup):
    step1 = State()


@user_router.message(ChangeLimits.step1)
async def change_limits1(message : types.Message, state : FSMContext, bot : Bot):
    temp = await message.answer(".", reply_markup=types.ReplyKeyboardRemove())
    await bot.delete_message(chat_id=message.chat.id, message_id=temp.message_id)
    if message.text == "⭐️ Звёзды":
        await state.set_state(ChangeStarLimits.step1)
        to_edit = await message.answer("🔽 Введите нижний порог для цены подарков.", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
    elif message.text == "📊 Саплай":
        await state.set_state(ChangeSupplyLimits.step1)
        to_edit = await message.answer("📊 Введи порог для саплая подарков.", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
    else:
        await state.clear()
        

@user_router.message(ChangeStarLimits.step1)
async def change_star_limits1(message : types.Message, state : FSMContext, bot : Bot):

    to_edit = await state.get_data()
    to_edit = to_edit["to_edit"]
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=to_edit, reply_markup=None)
    if message.text.isdigit():
        await state.update_data(down=message.text)
    else:
        to_edit = await message.answer("❌ Лимит должен быть числом!", reply_markup="cancel")
        await state.update_data(to_edit=to_edit.message_id)
        return
    
    to_edit = await message.answer("🔼 Введите верхний порог для цены подарков.", reply_markup=keyboards.cancel)
    await state.set_state(ChangeStarLimits.step2)
    await state.update_data(to_edit = to_edit.message_id)


@user_router.message(ChangeStarLimits.step2)
async def change_star_limits2(message : types.Message, state : FSMContext, bot : Bot):

    to_edit = await state.get_data()
    to_edit = to_edit["to_edit"]

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=to_edit, reply_markup=None)
 
    if not message.text.isdigit():
        to_edit = await message.answer("❌ Лимит должен быть числом!", reply_markup=keyboards.cancel)
        await state.update_data(to_edit=to_edit.message_id)
        return
    
    data = await state.get_data()

    down = data["down"]
    up = message.text

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET stars_limit=? WHERE user_id=?", (f"{down}-{up}", message.from_user.id, ))
        await db.commit()

    await message.answer("Ваши лимиты успешно обновлены!\n\nГлавное меню - /menu")
    await state.clear()


@user_router.message(ChangeSupplyLimits.step1)
async def change_supply_limits(message : types.Message, state : FSMContext, bot : Bot):

    to_edit = await state.get_data()
    to_edit = to_edit["to_edit"]

    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=to_edit, reply_markup=None)


    if not message.text.isdigit():
        to_edit = await message.answer("❌ Лимит должен быть числом!", reply_markup="cancel")
        await state.update_data(to_edit=to_edit.message_id)
        return
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET supply_limit=? WHERE user_id=?", (int(message.text), message.from_user.id, ))
        await db.commit()

    await message.answer("Вы успешно обновили лимит саплая на подарки.\n\nГлавное меню - /menu")
    await state.clear()



class Help(StatesGroup):
    step = State()


@user_router.message(Command("help"))
async def help(message : types.Message, state : FSMContext):

    to_edit = await message.answer("Здесь вы можете написать свое <b>обращение</b> нашим модераторам.\n\n<i>Время ответа может колебаться от 1 минуты до 1 часа.</i>", parse_mode="HTML", reply_markup=keyboards.cancel)
    await state.set_state(Help.step)
    await state.update_data(to_edit=to_edit.message_id)

@user_router.message(Help.step)
async def help2(message : types.Message, state : FSMContext, bot : Bot):

    temp = await state.get_data()
    to_edit = temp["to_edit"]
    await bot.edit_message_reply_markup(chat_id = message.chat.id, message_id=to_edit, reply_markup=None)

    await bot.send_message(chat_id=1404205394, text=f"Новое обращение от {message.from_user.full_name} (@{message.from_user.username})\n\n{message.text}", reply_markup=await keyboards.answer(message.from_user.id, message.message_id))
    
    await message.reply("Ваше сообщение было отправлено модераторам, ожидайте ответа!")



@user_router.message(Answer.step)
async def answer(message : types.Message, state : FSMContext, bot : Bot):

    text = message.text
    temp = await state.get_data()
    to_edit = temp["to_edit"]
    to_edit2 = temp["to_edit2"]
    chat_id = temp["chat_id"]
    message_id = temp["message_id"]
    previous_text = temp["previous_text"]


    text = "<b>Вам пришел ответ от модерации!</b>\n\n" + text

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

    await bot.send_invoice(chat_id=message.chat.id,
                           title="Депозит",
                           description=f"Пополнение баланса на {message.text} звёзд",
                           currency="XTR",
                           prices=[types.LabeledPrice(label=f"{message.text} звёзд", amount=amount)],
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


        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (int(amount * 0.9), message.from_user.id, ))
        
        for_admins = int(amount * 0.10)

        if referal_user_id != None:
            for_admins = int(amount * 0.05)
            balance = await db.execute("SELECT balance FROM users WHERE user_id=?", (referal_user_id, ))
            balance = await balance.fetchone()
            balance = balance[0]


            await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (int(amount * 0.05), referal_user_id, ))
            await bot.send_message(referal_user_id, f"Один из ваших друзей воспользовался вашей реферальной ссылкой и вы получили % от его депозита.\n\nВаш баланс: <strike>{balance}</strike> {balance + int(amount * 0.05)}", parse_mode="HTML")

        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (for_admins, 1404205394, ))

        await db.commit()




@user_router.message(Command("gift"))
async def gift(message : types.Message, bot : Bot):

    await bot.send_gift(user_id=message.from_user.id, gift_id="5170233102089322756", text="From sheazure")
