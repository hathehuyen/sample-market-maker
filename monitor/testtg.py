from telegram import Bot, ParseMode, ReplyKeyboardMarkup, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CommandHandler, Updater
import settings
from time import sleep
updater = Updater(token=settings.telegram_token)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

while True:
    sleep(10)
