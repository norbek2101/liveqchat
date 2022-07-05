from django.contrib import admin
from accounts.models import Operators


@admin.register(Operators)
class OperatorsAdmin(admin.ModelAdmin):
    list_display = ('id', 'slavebot', 'operator_id', 'is_online', 'date_online')
    list_editable = ( 'slavebot', 'is_online', 'date_online')
