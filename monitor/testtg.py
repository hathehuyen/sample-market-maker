from telegram import Bot, ParseMode, ReplyKeyboardMarkup, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CommandHandler, Updater
import settings
from time import sleep


class TG(object):
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self._updater: Updater = None

    def _init(self):
        self._updater = Updater(token=settings.telegram_token)
        self._dispatcher = self._updater.dispatcher
        start_handler = CommandHandler('start', self.start)
        self._dispatcher.add_handler(start_handler)
        self._updater.start_polling()

    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

tg = TG(settings.telegram_token, settings.chat_id)

while True:
    sleep(10)
