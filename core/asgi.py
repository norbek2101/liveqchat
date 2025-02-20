"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import django

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


from core.middleware import JWTAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from liveqchat.routing import websocket_urlpatterns




application = ProtocolTypeRouter(
                                {
                                    "http": get_asgi_application(),
                                    "websocket": JWTAuthMiddlewareStack(
                                                                        URLRouter(websocket_urlpatterns)
                                                                        )
                                }
                                )
