from django.db.models.signals import post_save, post_delete
from loguru import logger
from bot.models import SlaveBot, IncomingMessage
from bot.extra_func import send_to_operator
from bot.factory import bot_initializer
from django.dispatch import receiver
from django.conf import settings
from loguru import logger as lg
from telebot import TeleBot




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


# @receiver(post_save, sender=IncomingMessage)
# def msg_created(sender, instance: IncomingMessage, created, **kwargs):
#     if created:
#         if instance.is_sent:
#             return False
#         print("signals.py")
#         send_to_operator(instance, lg)
