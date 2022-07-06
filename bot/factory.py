from telebot.types import BotCommand
from telebot import TeleBot

from bot.handlers.chosen_inline_result import initializer_chosen_inline_result_handlers
from bot.utils.constants import SLAVE_BOT_COMMANDS

from bot.handlers.message import initializer_message_handlers
from bot.handlers.callback_query import initializer_callback_query_handlers
from bot.handlers.inline_query import initializer_inline_query_handlers
from bot.handlers.channel_post import initializer_channel_post_handlers
from bot.handlers.pre_checkout_query_handler import initializer_pre_checkout_query_handlers
from django.conf import settings
from pyngrok import ngrok


init = True

def get_ngrok_url():
    ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
    https_tunnel = ngrok.connect(8000, bind_tls=True)
    print(https_tunnel.public_url)
    BASE_URL = https_tunnel.public_url
    return BASE_URL


def bot_initializer(token):
    bot: TeleBot = TeleBot(token, parse_mode='html')

    if init:
        if not settings.BASE_URL:
            settings.BASE_URL = get_ngrok_url()

        print(bot.set_webhook(f"{settings.BASE_URL}/bot/{token}/"))
        print(bot.set_my_commands([BotCommand(command['command'], command['description']) for command in SLAVE_BOT_COMMANDS]))
    
    initializer_message_handlers(bot)
    initializer_callback_query_handlers(bot)
    initializer_inline_query_handlers(bot)
    initializer_channel_post_handlers(bot)
    initializer_pre_checkout_query_handlers(bot)
    initializer_chosen_inline_result_handlers(bot)

    return bot
