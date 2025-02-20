from dataclasses import fields
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from bot.models import BotUser, SlaveBot, IncomingMessage, BlackList, File
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import password_validation
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import  force_str
from rest_framework import serializers
from accounts.models import Operators
from django.utils.translation import gettext as _




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length = 12)
    class Meta:
        model = Operators
        fields = ('operator_id', 'password')


class BotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = (
                  'firstname', 'lastname', 'username',
                  'photo', 'email', 'phone_number', 'chat_id'
                )


class SlaveBotSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(format="%Y_%m_%d")
    class Meta:
        model = SlaveBot
        fields = (
                   'id', 'token', 'name', 'photo', 'username',
                   'description', 'information_text', 'first_msg'
        )
        extra_kwargs = {'token': {'required':False}}


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operators
        fields = (
                    'operator_id', 'first_name', 'last_name', 'username',
                    'photo', 'email', 'phone_number'
                 )
        extra_kwargs = {'photo': {'required':False}, 'operator_id': {'read_only': True}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotUser
        fields = (
            'firstname', 'lastname', 'photo', 'chat_id'
        )

class AddOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operators
        fields = (
                    'operator_id',
                )


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = (
            'id',
            'file',
            'type'
        )


# class IncomingMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IncomingMessage
#         fields = (
#             'slavebot', 'user', 'answer',
#             'message_id', 'message', 'created_at'
#         )

class ChatListSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = IncomingMessage
        fields = (
            'id', 'user', 'message', 'created_at', 'slavebot', 'file', 'is_sent', 'is_read', 'from_user', 'from_operator'
            )
        extra_kwargs = {'user': {'required':False}, 'operator_id': {'read_only': True}}

    def get_file(self, obj):
        files = obj.file.all()
        serializer = FileSerializer(files, many = True)
        if serializer.data == []:
            return None
        else:
            return serializer.data

    def to_representation(self, instance):
        unread_count = IncomingMessage.objects.filter(user=instance.user, is_read=False).count()
        representation = super().to_representation(instance)
        representation['name'] = f"{instance.user.firstname} {instance.user.lastname}"
        representation['unread_count'] = unread_count
        representation['user'] = instance.user.chat_id
        return representation




class ChatSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField(read_only = True)

    class Meta:
        model = IncomingMessage
        fields = (
            'id', 'message', 'operator' , 'file', 'created_at', 'user', 'message_id', 'from_user', 'from_operator'

        )
        extra_kwargs = {'user': {'required':False}, 'operator_id': {'read_only': True}, 'message_id': {'read_only': True}}

    def get_file(self, obj):
        print(obj,"\n\n\n\n\n")
        files = obj.file.all()
        serializer = FileSerializer(files, many = True)

        if serializer.data == []:
            return None
        else:
            return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['photo'] = str(instance.photo)
        representation['name'] = f"{instance.user.firstname} {instance.user.lastname}"
        return representation


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomingMessage
        fields = (
            'user', 'message', 'created_at'
        )
        extra_kwargs = {'user': {'required':False}, 'operator_id': {'read_only': True}}

    def to_representation(self, instance):
        unread_count = IncomingMessage.objects.filter(user=instance.user, is_read=False).count()
        representation = super().to_representation(instance)
        representation['name'] = f'{instance.user.firstname} {instance.user.lastname}'
        representation['unread_count'] = unread_count
        return representation


class SendMessageSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = IncomingMessage
        fields = ('id', 'message', 'chat_id', 'slavebot', 'created_at', 'message_id', 'from_user', 'from_operator')
        
        extra_kwargs = {
            'message_id': {
                'read_only': True
            }
        }
        
    def validate(self, attrs):
        super().validate(attrs)

        chat_id = attrs['chat_id']
        slave_bot = self.context.slavebot

        if not slave_bot:
            raise serializers.ValidationError({'slavebot': 'slavebot not exist !'}) 
        else:
            bot_users = slave_bot.users.filter(chat_id=chat_id)
            print("bot users",bot_users)
            if not bot_users.exists():
                raise serializers.ValidationError({'chat_id': "chat_id not exist !"})
        return attrs
    
    def create(self, validated_data):
        chat_id = validated_data.pop('chat_id')
        slave_bot = self.context.slavebot
        user = BotUser.objects.filter(chat_id=chat_id)
        validated_data['user'] = user[0]
        validated_data['slavebot'] = slave_bot
        validated_data['operator'] = self.context
        return super().create(validated_data)  

    def to_representation(self, instance):
        unread_count = IncomingMessage.objects.filter(user=instance.user, is_read=False).count()
        representation = super().to_representation(instance)
        representation['name'] = f"{instance.user.firstname} {instance.user.lastname}"
        representation['unread_count'] = unread_count
        representation['user'] = instance.user.chat_id
        return representation


class SavePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'file', 'created_at')


class SaveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'file', 'created_at')


class SendPhotoSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = IncomingMessage
        # fields = ('id', 'photo', 'slavebot', 'chat_id', 'created_at', 'message_id')
        fields = ('id', 'file', 'slavebot', 'chat_id')

        # extra_kwargs = {
        #         'message_id': {
        #             'read_only': True
        #         }
        #     }
        
    # def validate(self, attrs):
    #     super().validate(attrs)

    #     chat_id = attrs['chat_id']
    #     slave_bot = self.context.slavebot

    #     if not slave_bot:
    #         raise serializers.ValidationError({'slavebot': 'slavebot not exist !'}) 
    #     else:
    #         bot_users = slave_bot.users.filter(chat_id=chat_id)
    #         if not bot_users.exists():
    #             raise serializers.ValidationError({'chat_id': "chat_id not exist !"})
    #     return attrs
    
    # def create(self, validated_data):
    #     chat_id = validated_data.pop('chat_id')
    #     slave_bot = self.context.slavebot
    #     user = BotUser.objects.get(chat_id=chat_id)
    #     validated_data['user'] = user
    #     validated_data['slavebot'] = slave_bot
    #     validated_data['operator'] = self.context
    #     return super().create(validated_data) 

    # def to_representation(self, instance):
        # unread_count = IncomingMessage.objects.filter(user=instance.user, is_read=False).count()
        # representation = super().to_representation(instance)
        # representation['name'] = f"{instance.user.firstname} {instance.user.lastname}"
        # representation['unread_count'] = unread_count
        # representation['user'] = instance.user.chat_id
        # representation['chat_id'] = instance.slavebot.owner_id
        # return self.to_representation(instance)


class SendFileSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = IncomingMessage
        fields = ('id', 'chat_id', 'slavebot')
        # fields = ('id', 'file', 'chat_id', 'slavebot', 'created_at', 'message_id')

    #     extra_kwargs = {
    #         'message_id': {
    #             'read_only': True
    #         }
    #     }
        
    # def validate(self, attrs):
    #     super().validate(attrs)

    #     chat_id = attrs['chat_id']
    #     slave_bot = self.context.slavebot

    #     if not slave_bot:
    #         raise serializers.ValidationError({'slavebot': 'slavebot not exist !'}) 
    #     else:
    #         bot_users = slave_bot.users.filter(chat_id=chat_id)
    #         if not bot_users.exists():
    #             raise serializers.ValidationError({'chat_id': "chat_id not exist !"})
    #     return attrs
    
    # def create(self, validated_data):
    #     chat_id = validated_data.pop('chat_id')
    #     slave_bot = self.context.slavebot
    #     user = BotUser.objects.get(chat_id=chat_id)
    #     validated_data['user'] = user
    #     validated_data['slavebot'] = slave_bot
    #     validated_data['operator'] = self.context
    #     return super().create(validated_data) 

    # def to_representation(self, instance):
    #     unread_count = IncomingMessage.objects.filter(user=instance.user, is_read=False).count()
    #     representation = super().to_representation(instance)
    #     representation['name'] = f"{instance.user.firstname} {instance.user.lastname}"
    #     representation['unread_count'] = unread_count
    #     representation['user'] = instance.user.chat_id
    #     return representation


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(max_length=16, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=16, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=16, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.' )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': ("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class BlackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackList
        fields = ['user']
    
    def to_representation(self, instance):
        return {
            'user_id': instance.user.chat_id,
            'firstname': instance.user.firstname,
            'lastname': instance.user.lastname,
        }


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=4)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = Operators.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
