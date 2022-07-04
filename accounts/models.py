from django.contrib.auth.models import AbstractUser
from accounts.managers import UserManager
from django.db import models
from bot.utils.abstract import BaseModel


class Operators(AbstractUser, BaseModel):
    slavebot = models.ForeignKey('bot.SlaveBot', on_delete=models.CASCADE, related_name='operators', null=True)
    operator_id = models.CharField("operator id", max_length=15, unique=True)
    username = models.CharField("username", max_length=200, null=True, unique=True)
    photo = models.ImageField(null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    is_operator = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
        
    class Meta:
        verbose_name = "Operator"
        verbose_name_plural = "Operatorlar"
    
    USERNAME_FIELD = 'operator_id'
    objects = UserManager()
