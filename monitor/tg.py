# pragma pylint: disable=unused-argument, unused-variable, protected-access, invalid-name

"""
This module manage Telegram communication
"""
import logging
from typing import Any, Callable, Dict

# from tabulate import tabulate
from telegram import Bot, ParseMode, ReplyKeyboardMarkup, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CommandHandler, Updater


logger = logging.getLogger(__name__)

logger.debug('Included module telegram ...')


def authorized_only(command_handler: Callable[[Any, Bot, Update], None]) -> Callable[..., Any]:
    """
    Decorator to check if the message comes from the correct chat_id
    :param command_handler: Telegram CommandHandler
    :return: decorated function
    """
    def wrapper(self, *args, **kwargs):
        """ Decorator logic """
        update = kwargs.get('update') or args[1]

        # Reject unauthorized messages
        chat_id = int(self._config['telegram']['chat_id'])

        if int(update.message.chat_id) != chat_id:
            logger.info(
                'Rejected unauthorized message from: %s',
                update.message.chat_id
            )
            return wrapper

        logger.info(
            'Executing handler: %s for chat_id: %s',
            command_handler.__name__,
            chat_id
        )
        try:
            return command_handler(self, *args, **kwargs)
        except BaseException:
            logger.exception('Exception occurred within Telegram module')

    return wrapper


class Telegram(object):
    """  This class handles all telegram communication """

    def __init__(self, token, chat_id) -> None:
        """
        Init the Telegram call, and init the super class RPC
        :param freqtrade: Instance of a freqtrade bot
        :return: None
        """

        self._updater: Updater = None
        self._config = {'telegram': {'token': token, 'chat_id': chat_id}}
        self._init()

    def _init(self) -> None:
        """
        Initializes this module with the given config,
        registers all known command handlers
        and starts polling for message updates
        """
        self._updater = Updater(token=self._config['telegram']['token'], workers=0)

        # Register command handler and start telegram message polling
        handles = [
            CommandHandler('status', self._status),
            CommandHandler('position', self._position),
            CommandHandler('balance', self._balance),
            CommandHandler('help', self._help),
            CommandHandler('version', self._version),
        ]
        for handle in handles:
            self._updater.dispatcher.add_handler(handle)
        self._updater.start_polling(
            clean=True,
            bootstrap_retries=-1,
            timeout=30,
            read_latency=60,
        )
        logger.info(
            'rpc.telegram is listening for following commands: %s',
            [h.command for h in handles]
        )

    def cleanup(self) -> None:
        """
        Stops all running telegram threads.
        :return: None
        """
        self._updater.stop()

    @authorized_only
    def _help(self, bot: Bot, update: Update) -> None:
        """
        Handler for /help.
        Show commands of the bot
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        message = "*/start:* `Starts the trader`\n" \
                  "*/stop:* `Stops the trader`\n" \
                  "*/status [table]:* `Lists all open trades`\n" \
                  "         *table :* `will display trades in a table`\n" \
                  "*/profit:* `Lists cumulative profit from all finished trades`\n" \
                  "*/forcesell <trade_id>|all:* `Instantly sells the given trade or all trades, " \
                  "regardless of profit`\n" \
                  "*/performance:* `Show performance of each finished trade grouped by pair`\n" \
                  "*/daily <n>:* `Shows profit or loss per day, over the last n days`\n" \
                  "*/count:* `Show number of trades running compared to allowed number of trades`" \
                  "\n" \
                  "*/balance:* `Show account balance per currency`\n" \
                  "*/help:* `This help message`\n" \
                  "*/version:* `Show version`"

        self._send_msg(message, bot=bot)

    def send_msg(self, msg: str, bot: Bot = None,
                  parse_mode: ParseMode = ParseMode.MARKDOWN) -> None:
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
                    self._config['telegram']['chat_id'],
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
                    self._config['telegram']['chat_id'],
                    text=msg,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
        except TelegramError as telegram_err:
            logger.warning(
                'TelegramError: %s! Giving up on that message.',
                telegram_err.message
            )
