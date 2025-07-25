import traceback
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError


def setup_error_handler(dp, bot: Bot):
    ADMIN_ID = 1404205394
    @dp.error()
    async def global_error_handler(event, exception):
        tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        tb_short = tb[-4000:] if len(tb) > 4000 else tb

        msg = f"<b>‼️ Произошла ошибка</b>\n<pre>{tb_short}</pre>"

        try:
            await bot.send_message(chat_id=ADMIN_ID, text=msg)
        except TelegramAPIError as e:
            logging.error(f"Ошибка при отправке ошибки: {e}")

        logging.error(tb)
        return True
