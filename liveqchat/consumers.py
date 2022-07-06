from ast import operator
import json
from pytz import timezone
import telegram
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from json.decoder import JSONDecodeError
from requests import Response
from accounts.models import Operators
from bot.models import BotUser
from liveqchat.extra_ws_func import (
                            get_all_msg_list, get_search_message, get_all_msg_from_db,
                            filter_msg_by_user, send_msg_to_, get_bot_id, set_offline_status,
                            set_online_date_operator
                            )


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user', False)
        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()
        else:
            self.room_group_name = f"user_{user.id}"
            '''Join room group'''
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return  await self.send(json.dumps({"message": "User connected", "user": str(user)}))

    async def receive(self, text_data):
        """
        ACTIONS : 'create', 'get', 'get-list;
        """
        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(json.dumps({
                        'error': 'expected type json, got str instead'}))
        
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
        user = self.scope.get('user', False)
        ACTIONS = ['create', 'get', 'get-list']
        action = content.pop('action', False)

        if not action:
            return  await self.send_json({"errors": {"action": 'This field is required!'}})
       
        elif action == 'create':

            result = await send_msg_to_(self, content, user)
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    "data": result
                }
            )

        elif action == 'get':
            page = content.pop('page', False)
            page_size = content.pop('page_size', False)
            user_id = content.pop('user_id', False)
            bot_id = await get_bot_id(user)
            result = await filter_msg_by_user(user_id, bot_id, page, page_size)

            if not result:
                return await self.send_message("Page Not Found !")
            return await self.send_message({"data": result})

        elif action == 'get-list':
            oper_id = user.id
            try:
                result = await get_all_msg_from_db(oper_id)
            except Exception as e:
                return False
            return await self.send_message({"data": result})            
        else:
            return await  self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})


    async def send_message(self, event):
        data = event['data']
        await self.send_json(data)


    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            if not user.is_anonymous:
                await self.channel_layer.group_discard(
                            self.room_group_name,
                            self.channel_name
                        )
        except:
            pass
        finally:
            return await super().disconnect(code)

    def send_msg_to_bot(self, msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)


class SearchConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope.get('user', False)
        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()
        else:
            self.room_group_name = f"search_{user.id}"
            '''Join room group'''
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return  await self.send(json.dumps({"message": "User connected", "user": str(user.first_name)}))

    async def receive(self, text_data):
        """
        ACTIONS : 'get';
        """
        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return  await self.send(json.dumps({
                        'error': 'expected type json, got str instead'}))
        
        except JSONDecodeError as e:
            return  await self.send(json.dumps({'error': str(e)}))
        
        ACTIONS = ['get']
        action = content.pop('action', False)
        search_key = content.pop('key', False)

        if not action:
            return  await self.send_json({"errors": {"action": 'This field is required!'}})
        
        elif action == 'get':
            try:
                search_result = await get_search_message(search_key)
                data = {
                        "result": search_result
                       }
            except BotUser.DoesNotExist:
                return await Response("Not found")
            return  await self.send_message({"data": data})
        else:
            return  await self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})

    async def send_message(self, event):
        data = event['data']
        await self.send_json(data)


    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            if not user.is_anonymous:
                await self.channel_layer.group_discard(
                            self.room_group_name,
                            self.channel_name
                        )
        except:
            pass
        finally:
            return await super().disconnect(code)


class ChatListConsumer(AsyncJsonWebsocketConsumer):
    
    # def _get_connection_id(self):
    #     return ''.join(e for e in self.channel_name if e.isalnum())
    
    async def connect(self):
        operator = self.scope.get('user', False)
        await self.accept()

        if operator.is_anonymous:
            await self.send_json({"operator": str(operator), 'errors': operator.get_errors})
            return await self.close()
        else:
            await set_online_date_operator(operator.id)
            self.room_group_name = f"operator_{operator.id}"
            '''Join room group'''
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return  await self.send(json.dumps({"message": "operator connected", "operator": str(operator.id)}))


           
    async def receive(self, text_data):
        """ACTIONS : 'get'"""
        
        content = json.loads(text_data)
        await self.channel_layer.group_send(
                                            f"operator_{operator.id}", 
                                                        {
                                                        'type': 'send.data',
                                                        'data': content
                                                        }
                                            )
        try:
            if not isinstance(content, dict):
                return await self.send(json.dumps({
                        'error': 'expected type json, got str instead'}))
        
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
        operator = self.scope.get('user', False)
        ACTIONS = ['get']
        action = content.pop('action', False)

        if not action:
            return  await self.send_json({"errors": {"action": 'This field is required!'}})
        
        elif action == 'get':
            oper_id = operator.id
            
            try:
                result = await get_all_msg_from_db(oper_id)
            except Exception as e:
                return False
            return await self.send_data({"data": result})   
                 
        else:
            return await  self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})
   

    async def send_data(self, event):
        data = event['data']
        await self.send_json(content=await get_all_msg_list())


    async def disconnect(self, code):
        operator = self.scope.get('user', False)
        await set_offline_status(operator.id)
        try:
            if not operator.is_anonymous:
                await self.channel_layer.group_discard(
                                                        self.room_group_name,
                                                        self.channel_name
                                                       )
        except:
            pass
        finally:
            return await super().disconnect(code)
