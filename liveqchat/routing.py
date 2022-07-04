from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('chat/', consumers.ChatConsumer.as_asgi()),
    path('chat-search/', consumers.SearchConsumer.as_asgi()),
    path('chat-list/', consumers.ChatListConsumer.as_asgi())
]