import os
import uuid
import datetime
import pandas as pd
import telegram
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .serializers import (
                          AddOperatorSerializer, ChatListSerializer, ChatSerializer, OperatorSerializer, 
                          ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, 
                          SlaveBotSerializer, ChangePasswordSerializer, SendMessageSerializer, 
                          SendPhotoSerializer, BlackListSerializer
                           )
from bot.models import BotUser, IncomingMessage, SlaveBot, BlackList
from accounts.models import Operators
from api.send_email import Util
from api.paginations import ChatPagination
from collections import Counter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import  AllowAny, IsAuthenticated
from rest_framework import generics, status, filters
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from django.contrib.auth.hashers import make_password



class BotList(generics.ListAPIView):
    permission_classes = (AllowAny, )
    parser_classes = (FormParser, MultiPartParser)
    queryset = SlaveBot.objects.all()
    serializer_class = SlaveBotSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class BotDetail(APIView):
    permission_classes = (AllowAny, )
    parser_classes = (FormParser, MultiPartParser)

    @swagger_auto_schema(tags=["Bot"])
    def get_object(self, pk):
        try:
            return SlaveBot.objects.get(pk=pk)
        except SlaveBot.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        bot = self.get_object(pk)
        serializer = SlaveBotSerializer(bot)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SlaveBotSerializer)
    def patch(self, request, pk, format=None):
        bot = self.get_object(pk)
        serializer = SlaveBotSerializer(instance = bot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=SlaveBotSerializer)
    def delete(self, request, pk, format=None):
        bot = self.get_object(pk)
        bot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class OperatorList(generics.ListCreateAPIView):
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (AllowAny, )
    queryset = Operators.objects.all()
    serializer_class = OperatorSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    @swagger_auto_schema(request_body=AddOperatorSerializer)
    def post(self, request, format=None):
        serializer = AddOperatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                operator_obj = Operators.objects.get(operator_id = request.data['operator_id'])
                operator_obj.password = uuid.uuid4().hex[:12]
                pasword = operator_obj.password
                operator_obj.password = make_password(operator_obj.password)
                operator_obj.save()
            except Operators.DoesNotExist:
                raise Http404
            return Response({
                            'status':'Created successfully !',
                             'your password is' :f'{pasword}'},
                              status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OperatorDetail(APIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser, MultiPartParser)

    def get_object(self, operator_id):
        try:
            return Operators.objects.get(operator_id=operator_id)
        except Operators.DoesNotExist:
            raise Http404

    def get(self, request, operator_id):
        operator = self.get_object(operator_id)
        serializer = OperatorSerializer(operator)
        print(serializer)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OperatorSerializer)
    def patch(self, request, operator_id):
        op = self.get_object(operator_id)
        serializer = OperatorSerializer(op, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, operator_id):
        operator = self.get_object(operator_id)
        operator.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatList(generics.ListAPIView):
    permission_classes = (AllowAny, )
    pagination_class = ChatPagination

    queryset = IncomingMessage.objects.order_by('-created_at')
    serializer_class = ChatListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__firstname', 'user__lastname']


class ChatDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        bot_id = request.user.slavebot.id
        try:
             message = IncomingMessage.objects.filter(user__chat_id = chat_id, slavebot=bot_id)
        except:
            raise Http404
        serializer = ChatSerializer(message, many = True)
        return Response(serializer.data)


class DailyReport(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["Report"])
    def get(self, request, operator_id):

        """subatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))

        """xabarlar soni"""

        messages = IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               ).values_list('message')

        """xabarlarga javob berish uchun ketgan vaqt"""

        reply_time = IncomingMessage.objects.filter(
                                                operator__operator_id = operator_id,
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                                created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )
                                                
        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)
        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0

        
        data = {
            'suhbatlar_soni': len(convs),
            'xabarlar_soni': messages.count(),
            "aktivlik":f'{average_timedelta}s'
        }
        return Response(data)


class DashBoardDaily(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["DashBoard"])
    def get(self, request):

        """xabarlar soni"""
        messages = IncomingMessage.objects.filter(
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               ).count()
        operators = Operators.objects.all().count()

        """suhbatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))
        counter = 0
        for i in convs:
            counter+=1

        """xabarlarga javob berish uchun ketgan vaqt"""
        reply_time = IncomingMessage.objects.filter(
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0),
                                                created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )

        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)
        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0

        data = {
            'xabarlar_soni': messages,
            'operatorlar_soni': operators,
            'suhbatlar_soni': counter,
            "vaqt":f'{average_timedelta}s'
        }
        return Response(data)

 
class WeeklyReport(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(tags=["Report"])
    def get(self,request, operator_id):

        """subatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))
        """xabarlar soni"""
        messages = IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               ).values_list('message')

        """xabarlarga javob berish uchun ketgan vaqt"""
        reply_time = IncomingMessage.objects.filter(
                                                operator__operator_id = operator_id,
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                                created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )
        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)

        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0

        data = {
            'suhbatlar_soni': len(convs),
            'xabarlar_soni': messages.count(),
            "aktivlik":f'{average_timedelta}s'
        }
        return Response(data)


class DashBoardWeekly(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["DashBoard"])
    def get(self,request):

        """operatorlar soni"""
        operators = Operators.objects.all().count()

        """xabarlar soni"""
        messages = IncomingMessage.objects.filter(
                                        created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                        created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                        ).count()
        
        """suhbatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))
        counter = 0
        for i in convs:
            counter+=1

        """xabarlarga javob berish uchun ketgan vaqt"""
        reply_time = IncomingMessage.objects.filter(
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )

        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)
        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0

        data = {
            'xabarlar_soni': messages,
            'operatorlar_soni': operators,
            'suhbatlar_soni': counter,
            "vaqt":f'{average_timedelta}s'
        }
        return Response(data)


class MonthlyReport(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=["Report"])
    def get(self,request, operator_id):

        """subatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))
        """xabarlar soni"""
        counter = 0
        for i in convs:
            counter+=1
        messages = IncomingMessage.objects.filter(
                                               operator__operator_id = operator_id,
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               ).values_list('message')

        """xabarlarga javob berish uchun ketgan vaqt"""
        reply_time = IncomingMessage.objects.filter(
                                                operator__operator_id = operator_id,
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                                created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )

        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)
        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0


        data = {
            'suhbatlar_soni': len(convs),
            'xabarlar_soni': messages.count(),
            "aktivlik":f'{average_timedelta}s'
        }
        return Response(data)


class DashBoardMonthly(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(tags=["DashBoard"])
    def get(self,request):

        """operatorlar soni"""
        operators = Operators.objects.all().count()

        """xabarlar soni"""
        messages = IncomingMessage.objects.filter(
                                        created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                        created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                        ).count()
        """suhbatlar soni"""
        convs = list(Counter(IncomingMessage.objects.filter(
                                               created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                               created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                               )))
        counter = 0
        for i in convs:
            counter+=1
        """xabarlarga javob berish uchun ketgan vaqt"""
        reply_time = IncomingMessage.objects.filter(
                                                created_at__date__gte=datetime.today().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=29),
                                                created_at__date__lte=datetime.today().replace(hour=23,minute=59,second=59,microsecond=59)
                                                )

        """message yuborilgan vaqt"""
        start_list =[]
        for i in reply_time:
           start_list.append(i.created_at)

        """messagega javob berilgan vaqt""" 
        end_list =[]
        for i in reply_time:
           end_list.append(i.updated_at)

        """xabarlarga javob berish uchun ketgan o'rtacha vaqt"""
        times = []
        for i, j in zip(start_list, end_list):
            times.append(j-i)
        if len(times) != 0:
            average_timedelta = (sum(times, timedelta(microseconds=0))/len(times)).total_seconds()
        else:
            average_timedelta = 0

        data = {
            'xabarlar_soni': messages,
            'operatorlar_soni': operators,
            'suhbatlar_soni': counter,
            "vaqt":f'{average_timedelta}s'
        }
        return Response(data)


class Statistics(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=["Statistics"])
    def get(self, request):
        data = {
                'vaqt': [ 
                   timezone.now().replace(hour=i,minute=0,second=0,microsecond=0).replace(tzinfo=None) for i in range(24) 
                    ],
                        
                 'xabarlar_soni': [
                     IncomingMessage.objects.filter(
                                                    operator_id=request.user,
                                                    created_at__gte=timezone.now().replace(hour=i,minute=0,second=0,microsecond=0),
                                                    created_at__lte=timezone.now().replace(hour=i,minute=59,second=59,microsecond=59)
                                                    ).count() for i in range(24) 
                                   ]}
        # operator_id = Operators.objects.filter(id=request.user.id)\
        #               .values_list("operator_id", flat=True)[0]
        # print("operator_id", operator_id)
       
        # parent_dir = f"{settings.BOT_FILES}"
        
        # dir_name = f'{operator_id}//statistics/'
        # bot_path = os.path.join(parent_dir, dir_name)
        
        # if os.path.exists(bot_path):
        #     bot_path
        # else:
        #     os.makedirs(bot_path)
          
        df = pd.DataFrame(data)
        with pd.ExcelWriter("data.xlsx") as writer:
            df.to_excel(writer, index=False)
        return Response(df)



class BlackListView(APIView):
    permission_classes = (AllowAny,)
    
    @swagger_auto_schema(tags=['BlackList'])
    def get(self, request):
        blacklist = BlackList.objects.all()
        serializer = BlackListSerializer(blacklist, many = True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body =BlackListSerializer ,tags=["BlackList"])
    def post(self, request):
        try:
            user = BotUser.objects.get(chat_id=request.data['user'])

        except BotUser.DoesNotExist:
            return Response({'detail':'Bunday foydalanuvchi mavjud emas !'})

        blacklist = BlackList.objects.filter(user__chat_id = request.data['user'])
        if blacklist.exists():
            return Response({'detail':"Bu foydalanuvchi avval qora ro'yhatga qo'shilgan !"})
        else:
            BlackList.objects.create(user=user)
        return Response({'status':"Foydalanuvchi qora ro'yhatga qo'shildi ."})


class BlackListDetail(APIView):
    permission_classes = (AllowAny, )
    
    @swagger_auto_schema(tags=["BlackList"])
    def get_object(self, chat_id):
        try:
            return BotUser.objects.get(chat_id=chat_id)
        except BotUser.DoesNotExist:
            raise Http404

    @swagger_auto_schema(tags=["BlackList"])
    def delete(self, request, chat_id):
        user = self.get_object(chat_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ChangePasswordView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Updated successfully.'}, status=status.HTTP_200_OK)


class SendMessage(APIView):
    permission_classes = (IsAuthenticated,)

    def send_msg_to_bot(self, msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)
        
    @swagger_auto_schema(request_body=SendMessageSerializer, tags=["send-message"])
    def post(self, request):
        serializer = SendMessageSerializer(data=request.data, context=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        incmsg = IncomingMessage.objects.get(id=serializer.data['id'])
        botuser = BotUser.objects.get(id=serializer.data['user'])
        self.send_msg_to_bot(serializer.data['message'], botuser.chat_id, token=incmsg.slavebot.token)
        return Response('send successfully')


class SendPhoto(APIView):
    parser_classes = (FormParser, MultiPartParser)
    permission_classes  =(AllowAny, )
    my_token = '5116642374:AAEDrJjCfwaGpw9jc1lpEPwLxK_nS-v9rrQ'
    
    @swagger_auto_schema(request_body=SendPhotoSerializer, tags=["send-message"])
    def post(self, request, user_id):
        PHOTO_PATH = request.data['photo']
        serializer = SendPhotoSerializer(data = request.data, partial = True)
        if serializer.is_valid():
            bot = telegram.Bot(token=self.my_token)
            bot.send_photo(chat_id=user_id, photo=PHOTO_PATH)
            return Response({
                "status": "success"
            })
        else:
            return Response({'detail':'not found'})


class RequestPasswordResetEmail(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordEmailRequestSerializer

    @swagger_auto_schema(tags = ['Reset-password'])
    def post(self, request):

        email = request.data.get('email', '')

        if Operators.objects.filter(email=email).exists():
            user = Operators.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://127.0.0.1:8000' + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer


    @swagger_auto_schema(tags = ['Reset-password'])
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Operators.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response ({'error': 'Token is not valid, please request a new one .'})

            return Response ({'message': 'Credentials valid', 'uidb64':uidb64, 'token': token}, status=status.HTTP_200_OK)
            
        except DjangoUnicodeDecodeError as identifier:
            return Response ({'error': 'Token is not valid, please request a new one .'}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(tags = ['Reset-password'])
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


