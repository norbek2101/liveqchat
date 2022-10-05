from channels.layers import get_channel_layer
from accounts.models import Operators
from bot.models import IncomingMessage
from django.forms import model_to_dict
from asgiref.sync import async_to_sync
from django.db.models import Count, Q
from telebot import TeleBot
from loguru import logger as lg

def send_to_operator(instance: IncomingMessage, logger: lg):
    if instance.is_sent:
        return False
    channel_layer = get_channel_layer()
    data = model_to_dict(instance)
    # _data = data['message']
    print("data", data)
    obj = {}
    obj['id'] = data['id']
    obj['message'] = data['message']
    obj['slavebot'] = data['slavebot']
    obj['message_id'] = data['message_id']
    obj['from_user'] = data['from_user']
    obj['from_operator'] = data['from_operator']
    #obj['created_at'] = (data['created_at'])
    # print('dict--------------', data)
    
    bot_operators = Operators.objects.filter(
        slavebot=instance.slavebot,
        is_active=True
    )
   
    old_operators = bot_operators.annotate(
        total_msg=Count(
            'messages', filter=Q(
                messages__user=instance.user
                )
            )
    ).filter(total_msg__gt=0).order_by('-total_msg')

    offline_operator = bot_operators.filter(is_online=False).order_by("date_online")
    operator = None
    if old_operators.exists():
        operator = old_operators.first()
    else:
        online_operators = bot_operators.filter(
            is_online=True
        ).order_by('date_online')
        if online_operators.exists():
            operator = online_operators.first()
        else:
            operator = offline_operator.first()
    if operator is not None:
        try:
            print("extra func")
            instance.operator = operator
            print("instance.operator", instance.operator)
            async_to_sync(
                channel_layer.group_send)(
                                            f'operator_{operator.id}',
                                            {
                                                'type': 'send_data',
                                                'data':  data
                                            }
                                        )
            instance.is_sent = True
            if operator.username:
                operator: Operators
                chat_id: str = operator.username
                from_chat_id: str = instance.user.chat_id
                if not chat_id.startswith('@'):
                    chat_id = '@' + chat_id
                # if not from_chat_id.startswith('@'):
                #     from_chat_id = '@' + from_chat_id
                bot = TeleBot(instance.slavebot.token)
                # bot.forward_message(
                #     chat_id=632179390,
                #     from_chat_id=632179390,
                #     message_id=instance.message_id,
                # )
            instance.is_sent = True
        except Exception as e:
            print(e)
        finally:
            instance.save()
            
    return True

