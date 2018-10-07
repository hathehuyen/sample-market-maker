import logging
import threading
import json
from time import sleep
import settings
from monitor import Monitor
from telegram import Bot, ParseMode, ReplyKeyboardMarkup, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CommandHandler, Updater


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


mon = Monitor()
mon.start()


class Telegram(object):
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self._updater: Updater = None
        self._init()

    def _init(self):
        self._updater = Updater(token=self.token, workers=0)
        self._dispatcher = self._updater.dispatcher
        # Register command handler and start telegram message polling
        handles = [
            CommandHandler('status', self._status),
            CommandHandler('start', self._start),
            CommandHandler('position', self._position),
            CommandHandler('balance', self._balance),
            CommandHandler('help', self._help),
            CommandHandler('version', self._version),
        ]
        for handle in handles:
            self._dispatcher.add_handler(handle)

        # self._updater.start_polling(
        #     clean=True,
        #     bootstrap_retries=-1,
        #     timeout=30,
        #     read_latency=60,
        # )
        self._updater.start_polling()
        print('Telegram started')

    def _start(self, bot: Bot = None, update: Update = None):
        print('start')
        bot = bot or self._updater.bot
        bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

    def _status(self):
        print('status')
        if mon.bot_running:
            msg = 'Bot is running!'
        else:
            msg = 'Bot is stopped!'
        self._send_msg(msg)

    def _position(self):
        print('Position')

    def _balance(self):
        print('Balance')

    def _help(self):
        print('Version 0.99.9')

    def _version(self):
        print('Version 0.99.9')

    def _send_msg(self, msg: str, bot: Bot = None, parse_mode: ParseMode = ParseMode.MARKDOWN):
        """
        Send given markdown message
        :param msg: message
        :param bot: alternative bot
        :param parse_mode: telegram parse mode
        :return: None
        """
        bot = bot or self._updater.bot

        keyboard = [['/status', '/position', '/balance'],
                    ['/version', '/help']]

        reply_markup = ReplyKeyboardMarkup(keyboard)

        try:
            try:
                bot.send_message(
                    self.chat_id,
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                logger.warning(
                    'Telegram NetworkError: %s! Trying one more time.',
                    network_err.message
                )
                bot.send_message(
                    self.chat_id,
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        except TelegramError as telegram_err:
            logger.warning(
                'TelegramError: %s! Giving up on that message.',
                telegram_err.message
            )

    def send_msg(self, msg):
        self._send_msg(msg)


tg = Telegram(settings.telegram_token, settings.telegram_chat_id)


def check_running():
    interval = 1
    last_status = False
    while True:
        try:
            if last_status != mon.bot_running:
                last_status = mon.bot_running
                if mon.bot_running:
                    tg.send_msg('Bot is now running')
                else:
                    tg.send_msg('Bot is now stopped')
            sleep(interval)
        except Exception as ex:
            print(ex)


check_running_thread = threading.Thread(target=lambda: check_running())
check_running_thread.daemon = True
check_running_thread.start()

while True:
    sleep(60)

