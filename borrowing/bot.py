import decimal
import os
import time
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import filters
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=["start"])
async def send_notification(message: types.Message) -> None:
    notification_text = f"Hi"
    await message.reply(text=notification_text)


def send_telegram_notification(notification_text: str) -> None:
    bot.send_message(chat_id=CHAT_ID, text=notification_text)


@dp.message_handler(filters.Text(contains="hello"))
async def send_notification(message: types.Message) -> None:
    user_username = message.from_user.username
    chat_id = message.chat.id
    notification_text = f"Hi, {user_username}\n"
    await bot.send_message(chat_id=chat_id, text=notification_text)


# @dp.message_handler(filters.Text(contains="book"))
# async def send_notification(message: types.Message, borrowing: Borrowing) -> None:
#     user_username = message.from_user.username
#     notification_text = (
#                          f"Borrow date: {datetime.now()}\n"
#                          f"Expected return date: {expected_return_date}\n"
#                          f"Book daily fee: {book_daily_fee}\n"
#                          f"Book: {book}")
#     await bot.send_message(chat_id=os.environ.get("CHAT_ID"), text=notification_text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
