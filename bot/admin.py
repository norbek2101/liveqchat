from django.contrib import admin
from bot import models


@admin.register(models.SlaveBot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'owner_id', 'reload', 'is_active')
    list_editable = ('username', 'owner_id', 'reload', 'is_active')


@admin.register(models.BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'firstname',
        'lastname',
        'username',
    ]
