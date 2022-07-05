from django.contrib import admin
from bot import models


@admin.register(models.SlaveBot)
class BotAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'username', 
        'owner_id', 
        'reload', 
        'is_active'
        )
    list_editable = (
        'username', 
        'owner_id', 
        'reload', 
        'is_active'
        )


@admin.register(models.BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'firstname',
        'lastname',
        'username',
        'slavebot',
        'from_main_bot',
        'step',
    )


@admin.register(models.IncomingMessage)
class IncomingMesageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'operator',
        'slavebot',
        'reply',
        'message',
        'photo',
        'is_read',
    )
    list_editable = (
        'user', 
        'operator',
        'slavebot'
    )