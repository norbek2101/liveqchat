from django.contrib import admin
from accounts.models import Operators
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin



# @admin.register(Operators)
# class OperatorsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'operator_id', 'is_online', 'date_online')
#     list_editable = ('is_online', 'date_online')


""" Operator Creation form from admin panel """


class OperatorCreationForm(forms.ModelForm):
    """A form for creating new operators. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Operators
        fields = ('email',)

    def clean_password2(self):
        """Check that the two password entries match"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Save the provided password in hashed format"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class OperatorChangeForm(forms.ModelForm):
    """A form for updating operators. Includes all the fields on
    the operator, but replaces the password field with admin's
    password hash display field."""
    
    class Meta:
        model = Operators
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        return self.initial["password"]


class OperatorAdmin(BaseUserAdmin):
    form = OperatorChangeForm
    add_form = OperatorCreationForm

    # list_display = (
    #                 'id', "operator_id", 'first_name',
    #                 'last_name', 'username', 'phone_number',
    #                 'email', 'photo', 'is_operator', 'is_admin',
    #                 'date_online', 'is_online'
    #                 )
    list_display = ('id', 'operator_id', 'is_online', 'date_online')
    
    # list_editable = (
    #                  'email', 'photo','first_name',
    #                  'last_name', 'is_operator', 'is_admin',
    #                  'username', 'phone_number'
    #                  )
    list_editable = (
                        'is_online', 'date_online'
                    )
    
    list_filter = ('id',)
    fieldsets = (
        (None, {'fields': (
                            "operator_id", "first_name", "last_name",
                            "username", "email", "phone_number", 'is_active',
                            "is_operator", "is_admin", "photo", "is_online",
                            "date_online"
        )}),
        ('Bots_related', {'fields': ('slavebot',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('operator_id', 'password1', 'password2')}
        ),
    )
    search_fields = ('first_name', 'last_name', 'operator_id')
    ordering = ('id',)
    
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.picture.url} width="120" height="80"')