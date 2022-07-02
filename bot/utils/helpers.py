import hashlib
import traceback
from time import sleep

from django.utils import timezone
from requests import post
from telebot import TeleBot, types
from telebot.apihelper import ApiException

from bot.models import BotUser
from bot.utils.constants import CONSTANT


def upload_file(bot, file_id):
    downloaded_file = bot.download_file(bot.get_file(file_id).file_path)
    file_path = post('https://telegra.ph/upload', files={'file': ('file', downloaded_file, 'image/jpeg')}).json()[0]['src']
    return f"https://telegra.ph{file_path}"


def get_keyboard_markup(buttons, on_time=True):
    keyboard_markup = types.ReplyKeyboardMarkup(True, on_time)
    for row in buttons:
        if type(row) is list:
            keyboard_markup.add(*[types.KeyboardButton(button, request_contact=True if button.startswith("📞 ") else None) for button in row])
        else:
            keyboard_markup.add(types.KeyboardButton(row, request_contact=True if row.startswith("📞 ") else None))
    return keyboard_markup


def extract_full_name(message: types.Message):
    return f"{message.from_user.first_name}{f' {message.from_user.last_name}' if message.from_user.last_name else ''}"

