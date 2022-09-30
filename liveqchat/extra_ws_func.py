from ast import operator
from fileinput import filename
import os
import math
import telegram
from django.utils import timezone
from django.db.models import Q
from asgiref.sync import sync_to_async
from bot.models import BotUser, IncomingMessage, SlaveBot
from accounts.models import Operators
from api.serializers import (
                            ChatSerializer, SearchSerializer, 
                            ChatListSerializer, SendFileSerializer, SendMessageSerializer, SendPhotoSerializer
                            )


def remove_duplicate(q_set):
    my_list = []
    user_ids = list(set(q_set.values_list("user__id", flat=True)))
    for i in q_set:
        if i.user_id in user_ids:
           my_list.append(i)
           user_ids.remove(i.user_id)
        else:
            break
    return my_list


@sync_to_async
def get_search_message(search_key):
    msg = IncomingMessage.objects.filter(
                                            Q(user__firstname__contains=search_key) |
                                            Q(user__lastname__contains=search_key)).\
                                            order_by('user__firstname', 'user__lastname').\
                                            order_by('-created_at')
    msg_dublicate = remove_duplicate(msg)
    serializer = SearchSerializer(msg_dublicate, many=True)
    return serializer.data


@sync_to_async
def get_all_msg_from_db(operator_id):
    messages = IncomingMessage.objects.filter(operator_id=operator_id).order_by("-created_at")
    msg_duplicate = remove_duplicate(messages)
    serializer = ChatListSerializer(msg_duplicate, many=True)
    return serializer.data


@sync_to_async
def filter_msg_by_user(user_id, bot_id, operator, page=1, page_size=15):
    messages = IncomingMessage.objects.filter(operator=operator, user__chat_id=user_id, slavebot=bot_id).order_by("-created_at")
    if not messages:
        return {
            "result": "Messages does not exist"
            }
        
    pag_msg = messages[page_size*page-page_size:page*page_size][::-1]
    
    
    
    if page_size != 0:
        total_pages = math.ceil(messages.count()/page_size)
        serializer = ChatSerializer(pag_msg, many=True)

    else:
        total_pages = ''
        serializer = ChatSerializer(messages, many=True)
        
    if page*page_size > messages.count():
        serializer = ChatSerializer(pag_msg, many=True)
        
    return {
            "total_page": total_pages,
            "result": serializer.data
           }


@sync_to_async
def send_msg_to_user(content, user):
    serializer = SendMessageSerializer(data=content, context=user)
    if serializer.is_valid():
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        incmsg.from_operator = True
        incmsg.is_read = True
        incmsg.save()
        botuser = BotUser.objects.get(chat_id=serializer.data['user'])
        send_msg_to_bot(serializer.data['message'], botuser.chat_id, token=incmsg.slavebot.token)

        messages = IncomingMessage.objects.filter(operator=incmsg.operator,
                    user__chat_id=serializer.data['user'],
                    slavebot=incmsg.slavebot.id).order_by("-created_at")
        
        serializer1 = SendMessageSerializer(messages, many=True)
        return {"messages": serializer1.data[:15][::-1]}
    else:
        return serializer.errors  


def send_msg_to_bot(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)


@sync_to_async
def send_photo_to_user(content, user):
    serializer = SendPhotoSerializer(data=content, context=user)
    if serializer.is_valid():
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        incmsg.is_read = True
        incmsg.save()
        botuser = BotUser.objects.get(chat_id=serializer.data['user'])
        send_photo_to_bot(serializer.data['photo'], botuser.chat_id, token=incmsg.slavebot.token)
        return serializer.data
    else:
        return serializer.errors  


def send_photo_to_bot(PHOTO_PATH, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendPhoto(chat_id=chat_id, photo=open(os.getcwd()+PHOTO_PATH, "rb"))


@sync_to_async
def send_video_to_user(content, user):
    serializer = SendFileSerializer(data=content, context=user)
    if serializer.is_valid():
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        incmsg.is_read = True
        incmsg.save()
        botuser = BotUser.objects.get(chat_id=serializer.data['user'])
        send_video_to_bot(serializer.data['file'], botuser.chat_id, token=incmsg.slavebot.token)
        return serializer.data
    else:
        return serializer.errors  


def send_video_to_bot(_file, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendVideo(chat_id=chat_id, video=open(os.getcwd()+_file, "rb"))


@sync_to_async
def send_voice_to_user(content, user):
    serializer = SendFileSerializer(data=content, context=user)
    if serializer.is_valid():
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        incmsg.is_read = True
        incmsg.save()
        botuser = BotUser.objects.get(chat_id=serializer.data['user'])
        send_voice_to_bot(serializer.data['file'], botuser.chat_id, token=incmsg.slavebot.token)
        return serializer.data
    else:
        return serializer.errors    


def send_voice_to_bot(_file, chat_id, token):
    print("_file", _file)
    bot = telegram.Bot(token=token)
    bot.send_voice(chat_id=chat_id, voice=_file)

@sync_to_async
def get_bot_id(user):
    bot_id = SlaveBot.objects.get(id=user.slavebot.id)
    return bot_id


@sync_to_async
def get_all_msg_list():
    messages = IncomingMessage.objects.order_by("-created_at")
    msg_duplicate = remove_duplicate(messages)
    serializer = ChatListSerializer(msg_duplicate, many=True)
    return serializer.data


@sync_to_async
def create_operator_connection_id(operator_id, connection_id):
    pass
    # TODO operator connectionni to'girlash(o'chirib operators modeli bn ishlash) kerak
    # operator_create = OperatorConnection.objects.get_or_create(
    #                 operator_id=operator_id, connection_id=connection_id,
    #                 is_online=True)
    # return operator_create

@sync_to_async
def discard_operator_connection_id(operator_id):
    pass
    # TODO operator connectionni to'girlash(o'chirib operators modeli bn ishlash) kerak
    # operator_discards = OperatorConnection.objects.filter(operator_id=operator_id)
    # for operator_discard in operator_discards:
    #     operator_discard.delete()
    # return operator_discard

@sync_to_async
def online_operators():
    pass
    # TODO operator connectionni to'girlash(o'chirib operators modeli bn ishlash) kerak
    # online_opers = OperatorConnection.objects.filter(is_online=True)
    # serializer = OperatorConnectionSerializer(online_opers, many=True)
    # # print("online_opers", online_opers)
    # return serializer.data

@sync_to_async
def set_online_date_operator(operator_id):
    try:
        operator = Operators.objects.get(id=operator_id)
    except Operators.DoesNotExist:
        return "Error"
    operator.is_online = True
    operator.date_online = timezone.now()
    operator.save()
    return operator

@sync_to_async
def set_offline_status(operator_id):
    try:
        operator = Operators.objects.get(id=operator_id)
    except Operators.DoesNotExist:
        return "Error"
    operator.is_online = False
    operator.date_online = timezone.now()
    operator.save()
    return operator


@sync_to_async
def mark_as_read_chat_messages(user, bot_id):
    try:
        messages = IncomingMessage.objects.filter(user__chat_id=user, slavebot=bot_id, is_read=False)
        if messages:
            messages.update(is_read=True)
        return {'result': 'ok'}
    except:
        return {'result': 'Server error'}


@sync_to_async
def mark_as_read_chat_to_messages(user_id, bot_id, message_id):
    
    try:
        messages = IncomingMessage.objects.filter(user__chat_id=user_id, slavebot=bot_id, message_id__lte=message_id)
        
        if messages: 
            messages.update(is_read=True)
            
        return {'result': 'ok'}
    except Exception as e:
        return {'result': e}
