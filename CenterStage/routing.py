from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat import routing as core_routing
from .token_auth import TokenAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter({
    "websocket": AllowedHostsOriginValidator(TokenAuthMiddleware(
        URLRouter( 
            core_routing.websocket_urlpatterns
        )
    )
   )
})