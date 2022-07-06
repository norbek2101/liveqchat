from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import model_to_dict
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from bot.models import SlaveBot, IncomingMessage
from accounts.models import Operators
from bot.factory import bot_initializer
from django.conf import settings
from telebot import TeleBot
from django.db.models import Count, Q


@receiver(post_save, sender=SlaveBot)
def slavebot_save_handler(sender, instance: SlaveBot, created, **kwargs):
    print('signal func')
    if created and instance.is_active:
        bot = settings.BOTS.get(instance.token, False)
        if not bot:
            bot = bot_initializer(instance.token)
            settings.BOTS[instance.token] = bot
        bot_info = bot.get_me()
        instance.username = bot_info.username
        instance.name = bot_info.first_name
        instance.save()
    if instance.reload and instance.is_active:
        bot = settings.BOTS.get(instance.token, False)
        if not bot:
            bot = bot_initializer(instance.token)
            settings.BOTS[instance.token] = bot
        bot_info = bot.get_me()
        instance.username = bot_info.username
        instance.name = bot_info.first_name
        instance.reload = False
        instance.save()
    if not instance.is_active:
        try:
            bot: TeleBot = settings.BOTS.pop(instance.token)
            bot.delete_webhook()
        except:
            pass
    

@receiver(post_delete, sender=SlaveBot)
def slavebot_delete_handler(sender, instance: SlaveBot, **kwargs):
    try:
        bot: TeleBot = settings.BOTS.pop(instance.token)
        bot.delete_webhook()
    except:
        pass

  
@receiver(post_save, sender=IncomingMessage)
def msg_created(sender, instance: IncomingMessage, created, **kwargs):
    if created:
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
                print(operator.username)
                bot = TeleBot(instance.slavebot.token)
                bot.forward_message(
                    chat_id=operator.username,
                    from_chat_id=instance.user.chat_id,
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
