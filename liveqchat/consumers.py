import os
import json
import telegram
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from json.decoder import JSONDecodeError
from requests import Response
from bot.models import BotUser
from liveqchat.extra_ws_func import (
                            get_search_message, get_all_msg_from_db,
                            send_photo_to_user, send_video_to_user, send_voice_to_user, set_offline_status, set_online_date_operator,
                            filter_msg_by_user, mark_as_read_chat_messages, 
                            mark_as_read_chat_to_messages, send_msg_to_user, 
                            )
from rest_framework_simplejwt.backends import TokenBackend

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        operator = self.scope.get('user', False)
        await self.accept()

        if operator.is_anonymous:
            await set_offline_status(operator.id)
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
        operator = self.scope.get('user', False)
        self.room_group_name = f"operator_{operator.id}"
        
        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(json.dumps({
                        'error': 'expected type json, got str instead'}))
        
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
        
        operator = self.scope.get('user', False)
        ACTIONS = ['create', 'get', 'mark-as-read-message', 'mark-as-read-chat']
        action = content.pop('action', False)

        if not action:
            return  await self.send_json({"errors": {"action": 'This field is required!'}})
       
        elif action == 'send-message':

            result = await send_msg_to_user(content, operator)

            await self.channel_layer.group_send(
                f"operator_list_{operator.id}",
                {
                    'type': 'send_data',
                    "data": [result["messages"][len(result["messages"])-1]]
                }
            )
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_data',
                    "data": result
                }
            )
            
        elif action == 'send-photo':
            photo = content.pop("photo", False)
        
            if not photo:
                return await self.send_json({"errors": {"photo": 'This field is required!'}})
            
            result = await send_photo_to_user(content, operator)

            await self.channel_layer.group_send(
                f"operator_list_{operator.id}",
                {
                    'type': 'send_data',
                    "data": [result["messages"][len(result["messages"])-1]]
                }
            )
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_data',
                    "data": result
                }
            )

        elif action == 'send-voice':
            result = await send_voice_to_user(content, operator)

            await self.channel_layer.group_send(
                f"operator_list_{operator.id}",
                {
                    'type': 'send_data',
                    "data": [result["messages"][len(result["messages"])-1]]
                }
            )

            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_data',
                    "data": result
                }
            )
        
        elif action == 'send-video':
            result = await send_video_to_user(content, operator)

            await self.channel_layer.group_send(
                f"operator_list_{operator.id}",
                {
                    'type': 'send_data',
                    "data": [result["messages"][len(result["messages"])-1]]
                }
            )
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_data',
                    "data": result
                }
            )
        

        elif action == 'get':
            page = content.pop('page', False)
            if not page:
                return await self.send_data({"data": "Page Not Found !"})
            page_size = 15
            user_id = content.pop('user_id', False)
            operator = self.scope.get("user", False)
            bot_id = content.pop("bot_id", False)
            print(operator)

            return await self.send_data({"data": await filter_msg_by_user(user_id, bot_id, operator, page, page_size)})
        
        
        elif action == 'mark-as-read-chat':
            user_id = content.pop('user_id', False)
            bot_id = content.pop('bot_id', False)
            
            if not user_id:
                return await self.send_json({"errors": {"user_id": 'This field is required!'}})
            
            if not bot_id:
                return await self.send_json({"errors": {"bot_id": 'This field is required!'}})
            
            result = await mark_as_read_chat_messages(user_id, bot_id)
            return await self.send_data({"data": result})


        elif action == 'mark-as-read-message':
            user_id = content.pop('user_id', False)
            bot_id = content.pop('bot_id', False)
            message_id = content.pop('message_id', False)

            if not user_id:
                return await self.send_json({"errors": {"user_id": 'This field is required!'}})
            
            if not bot_id:
                return await self.send_json({"errors": {"bot_id": 'This field is required!'}})
                
            if not message_id:
                return await self.send_json({"errors": {"message_id": 'This field is required!'}})
            
            result = await mark_as_read_chat_to_messages(user_id, bot_id, message_id)
    
            return await self.send_data({"data": result})          


    async def send_data(self, event):
        data = event['data']
        await self.send_json(data)


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

    def send_msg_to_bot(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)



class SearchConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        operator = self.scope.get('user', False)
        await self.accept()

        if operator.is_anonymous:
            await set_offline_status(operator.id)
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
            
            return  await self.send_data({"data": data})
        else:
            return  await self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})

    async def send_data(self, event):
        data = event['data']
        await self.send_json(data)


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


class ChatListConsumer(AsyncJsonWebsocketConsumer):


    async def connect(self):
        operator = self.scope.get('user', False)
        await self.accept()

        if operator.is_anonymous:
            await set_offline_status(operator.id)
            await self.send_json({"operator": str(operator), 'errors': operator.get_errors})
            return await self.close()
        else:
            await set_online_date_operator(operator.id)
            self.room_group_name = f"operator_list_{operator.id}"
            '''Join room group'''
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return  await self.send(json.dumps({"message": "operator connected", "operator": str(operator.id)}))



    async def receive(self, text_data):
        """ACTIONS : 'get'"""
        
        operator = self.scope.get('user', False) 
        # await self.channel_layer.group_send(
        #                                     f"operator_{operator.id}", 
        #                                                 {
        #                                                 'type': 'send.data',
        #                                                 'data': content
        #                                                 }
        #                                     )
        try:
            content = json.loads(text_data)
            
            if not isinstance(content, dict):
                await set_offline_status(operator.id)
                return await self.send(json.dumps({
                        'error': 'expected type json, got str instead'}))
        
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
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
            return await self.send_list_data({"list_data": result})   
                 
        else:
            return await  self.send_json({'errors': {"action": f"enter one of the following : {ACTIONS}"}})
   

    async def send_data(self, event):
        data = event['data']
        await self.send_json(data)

    async def send_list_data(self, context):
        data = context['list_data']
        await self.send_json(data)

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
