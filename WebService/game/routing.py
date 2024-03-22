from django.urls import re_path
from . import off2pconsumers
from . import off4pconsumers
from . import offtourconsumers
from . import on2pconsumers

websocket_urlpatterns = [
	# Offline 1 vs 1
	re_path(r'ws/game/off/2p/(?P<room_name>\w+)/$', off2pconsumers.GameConsumer.as_asgi()),
	# Offline multiplay (4 players)
	re_path(r'ws/game/off/4p/(?P<room_name>\w+)/$', off4pconsumers.GameConsumer.as_asgi()),
	# Offline tournament
	re_path(r'ws/game/off/tour/(?P<room_name>\w+)/$', offtourconsumers.GameConsumer.as_asgi()),
	# Online 1 vs 1
	re_path(r'ws/game/on/2p/(?P<room_name>\w+)/$', on2pconsumers.GameConsumer.as_asgi()),
]
