from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import lawyer.routing
import client.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            lawyer.routing.websocket_urlpatterns +
            client.routing.websocket_urlpatterns
        )
    ),
})
