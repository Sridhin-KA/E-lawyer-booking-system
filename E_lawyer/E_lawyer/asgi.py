"""
ASGI config for HospitalManagement project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import lawyer.routing
from django.urls import path


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'E_lawyer.E_lawyer.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            lawyer.routing.websocket_urlpatterns
        )
    ),
})