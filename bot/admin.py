from django.contrib import admin
from bot import models
from django.utils.safestring import mark_safe


@admin.register(models.SlaveBot)
class BotAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'username', 
        'owner_id', 
        'reload', 
        'is_active',
        'created_at'
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
        'message_id',
        'photo',
        'file',
        'is_read',
    )
    list_editable = (
        'user', 
        'operator',
        'slavebot'
    )
@admin.register(models.File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'operator',
        'photo',
        'file'
    )
    list_editable = (
        'user', 
        'operator'
    )
    def get_image(self, obj):
        return mark_safe(f'<img src = {obj.photo.url} width = "120" height = "80">')