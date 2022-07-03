import telebot
import django
import sys
import os

# --------- < DJANGO SETUP > -----------
path_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(path_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
# --------  < / DJANGO SETUP > -------- 

from bot.utils.extra import MyStates, check_token, get_bots_list, make_keyboards, check_user, register_user
from telebot.storage import StatePickleStorage
from bot.models import BotUser, SlaveBot
from bot.utils.constants import Text, MAIN_BOT_COMMANDS
from telebot.types import BotCommand
from telebot import custom_filters
from django.conf import settings
from telebot import types
from telebot.types import ReplyKeyboardRemove

TOKEN = settings.BOT_TOKEN
state_storage = StatePickleStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)


@bot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    print('start_handler')
    bot.send_message(
        chat_id=message.chat.id, 
        text=Text.WELCOME, 
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove()
    )
    bot.set_state(message.chat.id, MyStates.main, message.chat.id)


@bot.message_handler(commands=['help'])
def help_handler(message: types.Message):
    print('help_handler')
    bot.send_message(
        chat_id=message.chat.id,
        text=Text.HELP,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove()
    )


@bot.message_handler(commands=['register'])
def register_handler(message: types.Message):
    print('register_handler')
    user, created = BotUser.objects.get_or_create(
            from_main_bot=True,
            chat_id=message.chat.id
        )
    is_registered = register_user(user, bot)
    if is_registered:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.ALREADY_REGISTER
        )


@bot.message_handler(commands=['mybots'])
def mybots_handler(message: types.Message):
    print('mybots_handler')
    result = check_user(message.chat.id)
    if not result:
        bot.send_message(
            chat_id=message.chat.id,
            text=Text.NOT_REGISTERED
        )
        return
    # slave_bots = SlaveBot.objects.filter(owner_id=message.chat.id)
    # bot_list = '\n'.join()    
    bot_list = get_bots_list(message.chat.id)
    if bot_list:
        bot.send_message(
            chat_id=message.chat.id,
            text=Text.BOT_LIST,
            reply_markup=bot_list
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=Text.BOTS_NOT_FOUND,
        )

# @bot.message_handler(state=MyStates.phone_number)
@bot.message_handler(content_types=['contact'])
def contact_handler(message: types.Message):
    print('contact_handler')
    user, created = BotUser.objects.get_or_create(
            from_main_bot=True,
            chat_id=message.chat.id
        )
    user: BotUser
    if message.content_type == 'contact':
        if message.contact.user_id == message.chat.id:
            user.__setattr__('phone_number', message.contact.phone_number)
            user.save()
            result = register_user(user, bot)
            if result:
                bot.send_message(
                    chat_id=user.chat_id,
                    text=Text.REGISTRATION_COMPLETED,
                    reply_markup=ReplyKeyboardRemove()
                )
                bot.set_state(user.chat_id, MyStates.main, user.chat_id)
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=Text.CONTACT_NOT_VALID
            )
    else:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.PHONE_NUMBER,
            reply_markup=make_keyboards('phone_number')
        )


@bot.message_handler(state=MyStates.first_name)
def first_name_handler(message: types.Message):
    print('first_name_handler')
    user, created = BotUser.objects.get_or_create(
            from_main_bot=True,
            chat_id=message.chat.id
        )
    user: BotUser
    user.__setattr__('firstname', message.text)
    user.save()
    result = register_user(user, bot)
    if result:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.REGISTRATION_COMPLETED,
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(user.chat_id, MyStates.main, user.chat_id)


@bot.message_handler(state=MyStates.last_name)
def last_name_handler(message: types.Message):
    print('last_name_handler')
    user, created = BotUser.objects.get_or_create(
            from_main_bot=True,
            chat_id=message.chat.id
        )
    user: BotUser
    user.__setattr__('lastname', message.text)
    user.save()
    result = register_user(user, bot)
    if result:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.REGISTRATION_COMPLETED,
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(user.chat_id, MyStates.main, user.chat_id)


@bot.message_handler(commands=['newbot'])
def newbot_handler(message: types.Message):
    print('newbot_handler')
    result = check_user(message.chat.id)
    if not result:
        bot.send_message(
            chat_id=message.chat.id,
            text=Text.NOT_REGISTERED
        )
        return
    bot.send_message(
        chat_id=message.chat.id,
        text=Text.NEWBOT
    )
    bot.set_state(message.chat.id, MyStates.newbot, message.chat.id)
    

@bot.message_handler(state=MyStates.newbot)
def bot_token_handler(message: types.Message):
    print('bot_token_handler')
    if message.content_type == 'text':
        token = message.text
        info = check_token(token)
        if isinstance(info, dict):
            slavebot, created = SlaveBot.objects.get_or_create(
                token=token,
                owner_id=message.chat.id
                )
            if created:
                slavebot.username = info['username']
                slavebot.name = info['name']
                slavebot.save()
                bot.send_message(
                    chat_id=message.chat.id,
                    text=Text.BOT_CREATED
                )
                bot.set_state(message.chat.id, MyStates.main, message.chat.id)
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=Text.BOT_ALREADY_CREATED
                )
                bot.set_state(message.chat.id, MyStates.main, message.chat.id)
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=Text.INVALID_TOKEN
            )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=Text.ENTER_TOKEN
        )


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

bot.set_my_commands(
        [
            BotCommand(command['command'], command['description'])
            for command in MAIN_BOT_COMMANDS
        ]
    )

bot.delete_webhook()
print(bot.get_me())
bot.infinity_polling(skip_pending=True)
