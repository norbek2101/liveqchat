from secrets import choice
from bot.utils.abstract import BaseModel
from django.db import models

from bot.utils.constants import STEP
import os
from django.core.exceptions import ValidationError

    
# def upload_path(instance, filename):
#     return f"{instance.staff.first_name}/{filename}"

FILE_TYPES = [
    ("document", "document"),
    ("image", "image"),
    ("audio", "audio"),
    ("media", "media")
]


class SlaveBot(BaseModel):
    token = models.CharField(max_length=400, unique=True)
    owner_id = models.PositiveBigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    reload = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(null=True,blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    information_text = models.CharField(max_length=1000, null=True, blank=True)
    first_msg = models.CharField(max_length=1000, null=True, blank=True)

    error_msg = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.username}"


class BotUser(BaseModel):
    slavebot = models.ForeignKey(SlaveBot, on_delete=models.SET_NULL, null=True, related_name='users')
    firstname = models.CharField("first name", max_length=200, null=True, blank=True)
    lastname = models.CharField("last name", max_length=200, null=True, blank=True)
    username = models.CharField("username", max_length=200, null=True)
    photo = models.ImageField(upload_to='botuser/', blank=True)
    email = models.EmailField(null=True, blank=True)
    chat_id = models.BigIntegerField("chat owner id", null=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    from_main_bot = models.BooleanField(default=False)
    step = models.PositiveSmallIntegerField(default=STEP.MAIN)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        verbose_name = 'Bot foydalanuvchisi'
        verbose_name_plural = 'Bot foydalanuvchilari'

    @classmethod
    def set_step(self, chat_id: int, step: str, token: str):
        try:
            bot_user: self = self.objects.get(
                chat_id=chat_id,
                slavebot__token=token
            )
            bot_user.step = step
            bot_user.save()
            return bot_user.step
        except self.DoesNotExist:
            return False

def validate_file_extension(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')


class IncomingMessage(BaseModel):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='messages', null= True)
    operator = models.ForeignKey('accounts.Operators', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    slavebot = models.ForeignKey(SlaveBot, on_delete=models.CASCADE, null=True, related_name='messages')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replied_messages', null=True, blank=True)
    message = models.CharField(max_length=5000, null=True)
    message_id = models.BigIntegerField('botdan yozilgan xabar IDsi', null=True, blank=True)
    file = models.ManyToManyField("File")
    from_user = models.BooleanField(default=False)
    from_operator = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.message} {self.created_at}'

    class Meta:
        verbose_name = "Kiruvchi sms"
        verbose_name_plural = "Kiruvchi smslar"
    

class BlackList(BaseModel):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name="blacklist")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
         return f'{self.user.chat_id} {self.user.lastname}'

    class Meta:
        verbose_name = "Qora ro'yhat"
        verbose_name_plural = "Qora ro'yhat"

class File(BaseModel):
    file = models.FileField(null=True, blank=True)
    type = models.CharField(max_length = 255, choices = FILE_TYPES, null = True, blank = True)
    duration = models.CharField(max_length = 255, null = True, blank = True)
    
    def __str__(self):
         return f'{self.type}'

    class Meta:
        verbose_name = "Fayl"
        verbose_name_plural = "Fayllar"
