from email.message import Message
import traceback
from threading import Thread
from telebot import types, TeleBot

from bot.utils.constants import STEP, LANGUAGE, CALLBACK, REASONS
from bot.models import BotUser, IncomingMessage, SlaveBot
from bot.utils.extra import make_keyboards, slavebot_register_user
from bot.utils.helpers import extract_full_name
from bot.utils.constants import Text, BtnText
from telebot.util import content_type_media


def initializer_message_handlers(_: TeleBot):
    def auth(handler, bot: TeleBot = _):
        def wrapper(message: types.Message, bot: TeleBot = bot):
            try:
                user: BotUser = BotUser.get(
                    chat_id=message.from_user.id,
                    slavebot__token=bot.token
                    )
                if user:
                    handler(message, user)
                else:
                    slavebot = SlaveBot.get(token=bot.token)
                    user: BotUser = BotUser.objects.create(
                        slavebot=slavebot,
                        chat_id=message.from_user.id,
                        username=message.from_user.username,
                    )
                    handler(message, user)
            except Exception as e:
                print(f'[ERROR] auth : {e}\n')
        return wrapper

    def check_user(chat_id: int, bot: TeleBot):
        try:
            user: BotUser = BotUser.objects.get(
                chat_id=chat_id,
                slavebot__token=bot.token
                )
        except BotUser.DoesNotExist:
            return False
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

    def check_step(message: types.Message, step):
        user: BotUser = BotUser.get(
            chat_id=message.from_user.id,
            slavebot__token=_.token
            )
        if user:
            return user.step == step
        else:
            return True

    @_.message_handler(commands=['start'])
    @auth
    def start_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        bot.send_message(
            chat_id=message.chat.id, 
            text=Text.WELCOME_SLAVE_BOT, 
            parse_mode='HTML',
            reply_markup=types.ReplyKeyboardRemove()
        )
        BotUser.set_step(message.chat.id, STEP.MAIN, bot.token)

    @_.message_handler(commands=['help'])
    def help_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        bot.send_message(
            chat_id=message.chat.id, 
            text=Text.HELP_SLAVE_BOT, 
            parse_mode='HTML',
            reply_markup=types.ReplyKeyboardRemove()
        )
        BotUser.set_step(message.chat.id, STEP.MAIN, bot.token)

    @_.message_handler(commands=['register'])
    @auth
    def register_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        try:
            is_registered = slavebot_register_user(user, bot)
            if is_registered:
                bot.send_message(
                    chat_id=user.chat_id,
                    text=Text.ALREADY_REGISTER
                )
        except Exception as e:
            print(f'[ERROR] register handler : {e}\n')

    @_.message_handler(
        content_types=content_type_media,
        func=lambda message: check_step(message, STEP.PHONE_NUMBER)
        )
    @auth
    def contact_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        if message.content_type == 'contact':
            if message.contact.user_id == message.chat.id:
                user.__setattr__('phone_number', message.contact.phone_number)
                user.save()
                result = slavebot_register_user(user, bot)
                if result:
                    bot.send_message(
                        chat_id=user.chat_id,
                        text=Text.REGISTRATION_COMPLETED_SLAVE_BOT,
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    BotUser.set_step(message.chat.id, STEP.MAIN, bot.token)
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

    @_.message_handler(
        content_types=content_type_media,
        func=lambda message: check_step(message, STEP.FIRST_NAME)
        )
    @auth
    def first_name_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        if message.content_type != 'text':
            bot.send_message(
                chat_id=user.chat_id,
                text=Text.FIRST_NAME,
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        user.__setattr__('firstname', message.text)
        user.save()
        result = slavebot_register_user(user, bot)
        if result:
            bot.send_message(
                chat_id=user.chat_id,
                text=Text.REGISTRATION_COMPLETED_SLAVE_BOT,
                reply_markup=types.ReplyKeyboardRemove()
            )
            BotUser.set_step(message.chat.id, STEP.MAIN, bot.token)

    @_.message_handler(
        content_types=content_type_media,
        func=lambda message: check_step(message, STEP.LAST_NAME)
        )
    @auth
    def last_name_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        if message.content_type != 'text':
            bot.send_message(
                chat_id=user.chat_id,
                text=Text.LAST_NAME,
                reply_markup=types.ReplyKeyboardRemove()
            )
        user.__setattr__('lastname', message.text)
        user.save()
        result = slavebot_register_user(user, bot)
        if result:
            bot.send_message(
                chat_id=user.chat_id,
                text=Text.REGISTRATION_COMPLETED_SLAVE_BOT,
                reply_markup=types.ReplyKeyboardRemove()
            )
            BotUser.set_step(message.chat.id, STEP.MAIN, bot.token)


    @_.message_handler(
        content_types=content_type_media,
        func=lambda message: check_step(message, STEP.MAIN)
        )
    @auth
    def message_handler(message: types.Message, user: BotUser, bot: TeleBot = _):
        result = check_user(message.chat.id, bot)
        if not result:
            bot.send_message(
                chat_id=message.chat.id,
                text=Text.NOT_REGISTERED
            )
            return
        bot.send_message(
            chat_id=message.chat.id,
            text=f'msg : {message.text}'
        )
        inc_msg = IncomingMessage.objects.create(
            user=user,
            slavebot=user.slavebot,
            message=message.text,
        )
        # TODO IncomingMessage obyekti socket orqali jo'natiladi

