from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from bot.models import SlaveBot
from bot.factory import bot_initializer
from django.conf import settings
from telebot import TeleBot


# def update_bot_info(bot, obj)
print('signal')
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
# def msg_created(sender, instance, created, **kwargs):
#     operators = OperatorConnection.objects.filter(is_online=True).values_list("operator_id", flat=True)
#     operator_incmsgs = IncomingMessage.objects.filter(operator_id__in=operators)\
#         .order_by("-created_at").values_list("operator_id", flat=True)
  
#     if created:
#         if operator_incmsgs.exists():
#             connection_id = OperatorConnection.objects.filter(
#                 operator_id=operator_incmsgs.first(), is_online=True)\
#                 .values_list("connection_id", flat=True)[0]
#             channel_layer = get_channel_layer()
#             data = model_to_dict(instance)
#             message = data['message']
#             async_to_sync(channel_layer.group_send)(
#                                                         f'operator_{connection_id}',
#                                                         {
#                                                             'type': 'send.data',
#                                                             'data': message
#                                                         }
#                                                     )
#         else:
#             operators = Operators.objects.all().values_list("operator_id", flat=True)[0]
#             print("operators",operators)
#             operator_incmsg = IncomingMessage.objects.filter(operator_id__in=operators)\
#                                                     .order_by("created_at").values_list("operator_id", flat=True)[0]
#             print("operator_incmsg", operator_incmsg)
#             channel_layer = get_channel_layer()
#             data = model_to_dict(instance)
#             message = data['message']
#             async_to_sync(channel_layer.group_send)(
#                                                         "operator",
#                                                         {
#                                                             'type': 'send.data',
#                                                             'data': message
#                                                         }
#                                                     )
        


# @receiver(post_save, sender=OperatorConnection)
# def oper_conn_created(sender, instance, created, **kwargs):  
#     if created: 
#         print("connection created")           
#         channel_layer = get_channel_layer()
#         data = model_to_dict(instance)
#         #message = data['message']
#         async_to_sync(channel_layer.group_send)(
#                                                     f"operator_{instance.connection_id}",
#                                                     {
#                                                         'type': 'send.data',
#                                                         'data': data
#                                                     }
#                                                 )
