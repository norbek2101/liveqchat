from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup
from telebot import types, TeleBot
from bot.models import BotUser, SlaveBot
from bot.utils.constants import Text, BtnText
from django.conf import settings


class MyStates(StatesGroup):
    register = State()
    phone_number = State()
    first_name = State()
    last_name = State()
    newbot = State()
    main = State()


def make_keyboards(key_type: str, row_with=1):
	markup = ReplyKeyboardMarkup(row_width=row_with, resize_keyboard=True)
	if key_type == 'phone_number':
		keys = [
			KeyboardButton(BtnText.BTN_PHONE_NUMBER, request_contact=True)
		]
		markup.add(*keys)
	return markup


def check_user(chat_id):
    user, created = BotUser.objects.get_or_create(
        from_main_bot=True,
        chat_id=chat_id
        )
    user: BotUser
    is_registered = all(
            (
                user.phone_number,
                user.firstname,
                user.lastname
            )
        )
    if not is_registered:
        return False
    return True


def register_user(user: BotUser, bot: TeleBot):
    user: BotUser
    if not user.phone_number:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.PHONE_NUMBER,
            reply_markup=make_keyboards('phone_number')
        )
        bot.set_state(user.chat_id, MyStates.phone_number, user.chat_id)
        return False

    if not user.firstname:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.FIRST_NAME,
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(user.chat_id, MyStates.first_name, user.chat_id)
        return False

    if not user.lastname:
        bot.send_message(
            chat_id=user.chat_id,
            text=Text.LAST_NAME,
            reply_markup=ReplyKeyboardRemove()
        )
        bot.set_state(user.chat_id, MyStates.last_name, user.chat_id)
        return False

    return True

def check_token(token):
    new_bot = TeleBot(token)
    try:
        res = new_bot.get_me()
        return True
    except:
        return False


def get_bots_list(chat_id):
    slave_bots = SlaveBot.objects.filter(owner_id=chat_id)
    inline_markup = InlineKeyboardMarkup(row_width=1)
    keys = []
    for slave_bot in slave_bots:
        slave_bot: SlaveBot
        keys.append(InlineKeyboardButton(slave_bot.name, url=slave_bot.username))
    inline_markup.add(*keys)
    result = False
    if keys:
        result = inline_markup
    return result
