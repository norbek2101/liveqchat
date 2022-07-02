# import telebot
# import django
# import sys
# import os

# path_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# sys.path.append(path_dir)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
# django.setup()
# from django.conf import settings
# from telebot.storage import StatePickleStorage


# TOKEN = settings.BOT_TOKEN
# state_storage = StatePickleStorage()
# bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

# from bot.utils.constants import Text
# from bot.utils.extra import MyStates, login_required


# @bot.message_handler(commands=['start'])
# @login_required
# def start_handler(message):
# 	bot.send_message(message.chat.id, Text.HELP_TEXT, parse_mode='HTML')


# def register_handler(update: Update, context: CallbackContext):
#     tg_user = update.effective_user
#     bot_user = BotUser.objects.filter(chat_id=tg_user.id).exists()
#     if bot_user:
#         update.message.reply_text(messages.ALREADY_REGISTER)
#         return ConversationHandler.END
#     else:
#         update.message.reply_text(messages.NAME)
#         return FIRST_NAME_STATE


# def first_name_handler(update: Update, context: CallbackContext):
#     message = update.message.text
#     tg_user = update.effective_user
#     bot_user, created = BotUser.objects.get_or_create(chat_id=tg_user.id)
#     bot_user.firstname = message
#     bot_user.username = tg_user.username
#     bot_user.save()
#     update.message.reply_text(messages.LASTNAME)
#     return LAST_NAME_STATE


# def last_name_handler(update: Update, context: CallbackContext):
#     message = update.message.text
#     tg_user = update.effective_user
#     bot_user = BotUser.objects.get(chat_id=tg_user.id)
#     bot_user.lastname = message
#     bot_user.save()

#     update.message \
#         .reply_text(messages.PHONE,
#                     reply_markup=ReplyKeyboardMarkup([
#         [KeyboardButton('Telefon raqam yuborish',
#                         request_contact=True)]
#         ], resize_keyboard=True, one_time_keyboard=True))
#     return PHONE_NUMBER_STATE

# def last_name_resend_handler(update: Update, context: CallbackContext):
#     update.message.reply_text(messages.LASTNAME_RESEND)


# def phone_number_handler(update: Update, context: CallbackContext):
#     tg_user = update.effective_user
#     message = update.message.text

#     try:
#             if message.startswith('+998') and len(message) == 13:
#                 user_obj = BotUser.objects.get(phone_number=message)

#             elif len(message) == 9 and message.isdigit():
#                 message = '+998'+ message
#                 user_obj = BotUser.objects.get(phone_number=message)
            
#             elif message.isdigit() and len(message) == 12:
#                 message = '+' + message
#                 user_obj = BotUser.objects.get(phone_number=message)
#             else:
#                 update.message.reply_text(messages.PHONE_FORMAT)
#             return PHONE_NUMBER_STATE
            
#     except BotUser.DoesNotExist:
#             bot_user, created = BotUser.objects.get_or_create(chat_id = tg_user.id)
#             bot_user.phone_number = message
#             bot_user.save()
#             update.message.reply_text(messages.REGISTER_COMPLETED, reply_markup=ReplyKeyboardRemove())
#     return ConversationHandler.END


# def contact_handler(update:Update, context:CallbackContext):
#     user = update.effective_user
#     user_obj = BotUser.objects.get(chat_id = user.id)
#     contact = update.message.contact.phone_number
#     phone_number = contact
#     user_obj.phone_number = phone_number
#     user_obj.save()
#     update.message.reply_text(messages.NEWBOT, reply_markup=ReplyKeyboardRemove())
#     return ConversationHandler.END


# def new_bot_handler(update :Update, context: CallbackContext):
#     tg_user = update.effective_user
#     user_obj = BotUser.objects.filter(chat_id = tg_user.id).exists()
#     if user_obj:
#         update.message.reply_text(messages.NEWBOT)
#     else:
#         update.message.reply_text(messages.NOT_REGISTERED)
#     return NEW_BOT_STATE
