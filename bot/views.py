from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telebot import TeleBot
from telebot.types import Update

from bot.factory import bot_initializer
from bot.models import SlaveBot
from django.conf import settings


active_bots = SlaveBot.objects.filter(is_active=True)

for bot in active_bots:
    bot: TeleBot = bot_initializer(bot.token)
    settings.BOTS[bot.token] = bot

print(settings.BOTS)

@csrf_exempt
def web_hook(request, token):
    print("working")
    bot: TeleBot = settings.BOTS.get(token, False)
    if bot:
        if request.headers.get('content-type') == 'application/json':
            json_string = request.body.decode('utf-8')
            update = Update.de_json(json_string)
            bot.process_new_updates([update])
            return JsonResponse({'ok': True})
        else:
            return JsonResponse({'ok': False, 'description': 'Incorrect format of content type.'})
    else:
        return JsonResponse({'ok': False, 'description': 'Incorrect token.'})
        # slave_bots = SlaveBot.objects.filter(
        #     is_active=True,
        #     token=token
        # )
        # if slave_bots.exists():
        #     bot: TeleBot = bot_initializer(token)
        #     settings.BOTS[token] = bot
        #     web_hook(request, token)
