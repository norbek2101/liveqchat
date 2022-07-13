from channels.layers import get_channel_layer
from accounts.models import Operators
from bot.models import IncomingMessage
from django.forms import model_to_dict
from asgiref.sync import async_to_sync
from django.db.models import Count, Q
from telebot import TeleBot



def send_to_operator(instance: IncomingMessage):
    print("send_operator")
    if instance.is_sent:
        return False
    channel_layer = get_channel_layer()
    data = model_to_dict(instance)
    message = data['message']
    bot_operators = Operators.objects.filter(
        slavebot=instance.slavebot,
        is_active=True
    )
    print("bot_operators", bot_operators)
   
    old_operators = bot_operators.annotate(
        total_msg=Count(
            'messages', filter=Q(
                messages__user=instance.user
                )
            )
    ).filter(total_msg__gt=0).order_by('-total_msg')

    offline_operator = Operators.objects.filter(is_online=False)
    operator = None
    if old_operators.exists():
        operator = old_operators.first()
        print("old_operators", old_operators)
        for i in old_operators:
            print("iiiiii",i.total_msg)
            
            for m in i.messages.all():
                print("m.user", m.user)
    else:
        online_operators = bot_operators.filter(
            is_online=True
        ).order_by('date_online')
        print("online_operators", online_operators)
        if online_operators.exists():
            operator = online_operators.first()
        else:
            ...
    print('operator : ', operator)
    if operator is not None:
        try:
            print("try")
            instance.operator = operator
            print("instance.operator", instance.operator)
            async_to_sync(
                channel_layer.group_send)(
                                            f'operator_{operator.id}',
                                            {
                                                'type': 'send.data',
                                                'data': message
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
                print("chat_id",type(chat_id))
                print("from_chat_id", type(from_chat_id))
                bot = TeleBot(instance.slavebot.token)
                bot.forward_message(
                    chat_id=632179390,
                    from_chat_id=632179390,
                    message_id=instance.message_id,
                )
            instance.is_sent = True
        except Exception as e:
            print(e)
        finally:
            instance.save()
            
    return True

