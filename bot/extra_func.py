from channels.layers import get_channel_layer
from accounts.models import Operators
from bot.models import IncomingMessage
from django.forms import model_to_dict
from asgiref.sync import async_to_sync
from django.db.models import Count, Q
from telebot import TeleBot



def send_to_operator(instance: IncomingMessage):
    if instance.is_sent:
        return False
    channel_layer = get_channel_layer()
    data = model_to_dict(instance)
    message = data['message']
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
    ).order_by('-total_msg')
    operator = None
    if old_operators.exists():
        operator = old_operators.first()
    else:
        online_operators = bot_operators.filter(
            is_online=True
        ).order_by('date_online')
        if online_operators.exists():
            operator = online_operators.first()
    print('operator : ', operator)
    if operator is not None:
        instance.operator = operator
        instance.save()
        if operator.username:
            operator: Operators
            chat_id: str = operator.username
            from_chat_id: str = instance.slavebot.username
            if not chat_id.startswith('@'):
                chat_id = '@' + chat_id
            if not from_chat_id.startswith('@'):
                from_chat_id = '@' + from_chat_id
            print(chat_id)
            print(from_chat_id)
            bot = TeleBot(instance.slavebot.token)
            bot.forward_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=instance.message_id,
            )
        async_to_sync(
            channel_layer.group_send)(
                                        f'operator_{operator.id}',
                                        {
                                            'type': 'send.data',
                                            'data': message
                                        }
                                    )
    return True

