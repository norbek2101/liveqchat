from bot.utils.extra import make_keyboards, slavebot_register_user
from bot.models import BotUser, File, IncomingMessage, SlaveBot, File
from bot.utils.constants import Text, BtnText
from telebot.util import content_type_media
from bot.extra_func import send_to_operator
from bot.utils.constants import STEP
from telebot import types, TeleBot
from loguru import logger as lg
from django.conf import settings
import logging
from accounts.models import (
    Operators
)
from django.db.models import Count


def get_bot_logger(token):
    try:
        slave_bot: SlaveBot = SlaveBot.objects.get(token=token)
        bot_date = slave_bot.created_at.strftime('%Y_%m_%d')
        file_name = f"{settings.BASE_DIR}/clients/{slave_bot.owner_id}/{token[:10]}_{bot_date}/debug.log"
        return lg.add(file_name)
    except Exception as e:
        logger = logging.getLogger('slavebot')
        logger.warning(f"bot writes logs to another file {e.args}")
        return logger



def initializer_message_handlers(_: TeleBot):
    logger = get_bot_logger(_.token)
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
                logger.error(e)
        return wrapper

    def check_user(chat_id: int, bot: TeleBot):
        try:
            user: BotUser = BotUser.objects.get(
                chat_id=chat_id,
                slavebot__token=bot.token
                )
        except BotUser.DoesNotExist:
            logger.info('bot user does not exist')
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
        try:
            user: BotUser = BotUser.get(
                chat_id=message.from_user.id,
                slavebot__token=_.token
                )
            if user:
                return user.step == step
            else:
                return True
        except BotUser.DoesNotExist as e:
            logger.error(e)

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
    def help_handler(message: types.Message, bot: TeleBot = _):
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
            logger.error(f"register handler : {e}")

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
        else:
            print("***", message.content_type)
            
            if message.content_type == 'document':
                
                file_name = message.document.file_name
                path = 'media/'+file_name
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open(path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                    
    
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Xabaringiz operatorlarga jo'natildi"
                )
                
                # if (user.slavebot.operator is None) or (user.slavebot.operator.is_online == False) or (user.slavebot.operator.is_active == False):
                #     operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                #     operator.slavebot = user.slavebot
                #     operator.save()
                    
                try:
                    
                    if user.slavebot.operators.first() is None:
                        operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                        slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                        operator.slavebot = slavebot
                        operator.save()
                    else:
                        operators = Operators.objects.get(operator_id = user.slavebot.operators.first())
                        if (operators.is_online == False) or (operators.is_active == False):
                                operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                                slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                                operator.slavebot = slavebot
                                operator.save()
                        else:
                            operator = Operators.objects.get(id = operators.id)
                except Exception as e:
                    print(e)


                inc_msg = IncomingMessage.objects.create(
                    user=user,
                    slavebot=user.slavebot,
                    message_id=message.message_id,
                    from_user=True,
                    operator=operator
                )

                up_file = File.objects.create(file = str(path).split('media/')[1], type = "audio")

                inc_msg.file.add(up_file)
                inc_msg.save()

                try:
                
                    send_to_operator(inc_msg, logger)
                except Exception as e:
                    logger.warning(e)
            
            elif message.content_type == 'photo':
            
                raw = message.photo[-1].file_id
                path = 'media/'+ raw + ".jpg"
                file_info = bot.get_file(raw)
                downloaded_file = bot.download_file(file_info.file_path)
                
                with open(path,'wb') as new_file:
                    new_file.write(downloaded_file)
                    
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Xabaringiz operatorlarga jo'natildi"
                )
                
                try:
                    
                    if user.slavebot.operators.first() is None:
                        operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                        slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                        operator.slavebot = slavebot
                        operator.save()
                    else:
                        operators = Operators.objects.get(operator_id = user.slavebot.operators.first())
                        if (operators.is_online == False) or (operators.is_active == False):
                                operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                                slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                                operator.slavebot = slavebot
                                operator.save()
                        else:
                            operator = Operators.objects.get(id = operators.id)
                except Exception as e:
                    print(e)


                inc_msg = IncomingMessage.objects.create(
                    user=user,
                    slavebot=user.slavebot,
                    message_id=message.message_id,
                    from_user=True,
                    operator=operator
                )
                
                up_file = File.objects.create(file = str(path).split('media/')[1], type = "audio")

                inc_msg.file.add(up_file)
                inc_msg.save()

                try:
                
                    send_to_operator(inc_msg, logger)
                except Exception as e:
                    logger.warning(e)

            elif message.content_type == 'text':
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Xabaringiz operatorlarga jo'natildi"
                )
                try:
                    
                    if user.slavebot.operators.first() is None:
                        operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                        slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                        operator.slavebot = slavebot
                        operator.save()
                    else:
                        operators = Operators.objects.get(operator_id = user.slavebot.operators.first())
                        if (operators.is_online == False) or (operators.is_active == False):
                                operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                                slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                                operator.slavebot = slavebot
                                operator.save()
                        else:
                            operator = Operators.objects.get(id = operators.id)
                except Exception as e:
                    print(e)

                inc_msg = IncomingMessage.objects.create(
                    user=user,
                    slavebot=user.slavebot,
                    message=message.text,
                    message_id=message.message_id,
                    from_user=True,
                    operator=operator
                )

                
                
                try:
                    send_to_operator(inc_msg, logger)
                except Exception as e:
                    logger.warning(e)
            
            elif message.content_type == 'voice':
                _file_name = message.voice.file_id
                path = 'media/'+_file_name + '.mp3'
                file_info = bot.get_file(_file_name)
                downloaded_file = bot.download_file(file_info.file_path)
                with open(path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                    
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Xabaringiz operatorlarga jo'natildi"
                )

                try:
                    
                    if user.slavebot.operators.first() is None:
                        operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                        slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                        operator.slavebot = slavebot
                        operator.save()
                    else:
                        operators = Operators.objects.get(operator_id = user.slavebot.operators.first())
                        if (operators.is_online == False) or (operators.is_active == False):
                                operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                                slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                                operator.slavebot = slavebot
                                operator.save()
                        else:
                            operator = Operators.objects.get(id = operators.id)
                except Exception as e:
                    print(e)


                inc_msg = IncomingMessage.objects.create(
                    user=user,
                    slavebot=user.slavebot,
                    message_id=message.message_id,
                    from_user=True,
                    operator = operator
                )

                up_file = File.objects.create(file = str(path).split('media/')[1], type = "audio")

                inc_msg.file.add(up_file)
                inc_msg.save()

                try:
                
                    send_to_operator(inc_msg, logger)
                except Exception as e:
                    logger.warning(e)
            
            elif (message.content_type == 'video') or (message.content_type == 'video_note'):
                
                if message.content_type == "video":
                    _file_name = message.video.file_id
                else:
                    _file_name = message.video_note.file_id

                path = 'media/'+ _file_name + '.mp4'
                file_info = bot.get_file(_file_name)
                downloaded_file = bot.download_file(file_info.file_path)
                with open(path, 'wb') as new_file:
                    new_file.write(downloaded_file)
                    
    
                bot.send_message(
                    chat_id=message.chat.id,
                    text="Xabaringiz operatorlarga jo'natildi"
                )


                try:
                    
                    if user.slavebot.operators.first() is None:
                        operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                        slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                        operator.slavebot = slavebot
                        operator.save()
                    else:
                        operators = Operators.objects.get(operator_id = user.slavebot.operators.first())
                        if (operators.is_online == False) or (operators.is_active == False):
                                operator = Operators.objects.filter(is_active = True).annotate(num_messages = Count("messages")).order_by("num_messages")[0]
                                slavebot = SlaveBot.objects.get(id = user.slavebot.id)
                                operator.slavebot = slavebot
                                operator.save()
                        else:
                            operator = Operators.objects.get(id = operators.id)
                except Exception as e:
                    print(e)

                
                inc_msg = IncomingMessage.objects.create(
                    user=user,
                    slavebot=user.slavebot,
                    # file=path,
                    message_id=message.message_id,
                    from_user=True,
                    operator = operator
                )

                up_file = File.objects.create(file = str(path).split('media/')[1], type = "audio")

                inc_msg.file.add(up_file)
                inc_msg.save()

                try:
                
                    send_to_operator(inc_msg, logger)
                except Exception as e:
                    logger.warning(e)