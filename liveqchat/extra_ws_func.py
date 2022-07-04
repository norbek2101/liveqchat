import math
from django.db.models import Q
from asgiref.sync import sync_to_async
from bot.models import BotUser, IncomingMessage, SlaveBot#, OperatorConnection
from api.serializers import (
                            ChatSerializer, SearchSerializer, SendMessageSerializer,
                            ChatListSerializer, OperatorConnectionSerializer
                            )


def remove_duplicate(q_set):
    my_list = []
    user_ids = list(set(q_set.values_list("user__id", flat=True)))
    print("user ids", user_ids)
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
    messages = IncomingMessage.objects.filter(operator_id=operator_id, is_read=False).order_by("-created_at")
    msg_duplicate = remove_duplicate(messages)
    serializer = ChatListSerializer(msg_duplicate, many=True)
    return serializer.data


@sync_to_async
def filter_msg_by_user(user_id, bot_id, page=1, page_size=10):
    messages = IncomingMessage.objects.filter(Q(user__chat_id=user_id), Q(slavebot=bot_id))
    
    if page*page_size > messages.count():
        return False
    
    pag_msg = messages[page*page_size-page_size:page*page_size]
    if page_size != 0:
        total_pages = math.ceil(messages.count()/page_size)
        serializer = ChatSerializer(pag_msg, many=True)

    else:
        total_pages = ''
        serializer = ChatSerializer(messages, many=True)

    return {
            "total_page": total_pages,
            "result": serializer.data
           }


@sync_to_async
def send_msg_to_(self, content, user):
    serializer = SendMessageSerializer(data=content, context=user)
    if serializer.is_valid():
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        incmsg.is_read = True
        incmsg.save()
        botuser = BotUser.objects.get(id=serializer.data['user'])
        self.send_msg_to_bot(serializer.data['message'], botuser.chat_id, token=incmsg.slavebot.token)
        return serializer.data
    else:
        result = {"errors": serializer.errors}
        return self.send_json(result)  


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