import logging
from config import DATE_FORMAT
import asyncio
from aiogram import Bot


class TelegramHandler(logging.Handler):
    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id
        self.loop = asyncio.get_event_loop()

    def emit(self, record):
        try:
            msg = self.format(record)
            # Используем ensure_future, чтобы не блокировать логгер
            asyncio.ensure_future(self.bot.send_message(chat_id=self.chat_id, text=msg))
        except Exception:
            self.handleError(record)    


logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("logs.log", encoding="UTF-8")


formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=DATE_FORMAT
)

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)