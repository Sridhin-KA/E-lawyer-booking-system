from django.urls import re_path
from .consumers import ClientCallConsumer

websocket_urlpatterns = [
    re_path(r'ws/call/(?P<client_id>\d+)/(?P<lawyer_id>\d+)/$', ClientCallConsumer.as_asgi()),
]
