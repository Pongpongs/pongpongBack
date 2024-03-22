from django.urls import re_path
from . import offoneconsumers
from . import offmulticonsumers
from . import ononeconsumers

websocket_urlpatterns = [
	# re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
	# Offline 1 vs 1
	re_path(r'ws/game/offline/oneversone/(?P<room_name>\w+)/$', offoneconsumers.GameConsumer.as_asgi()),
	# Offline multiplay (4 players)
	re_path(r'ws/game/offline/multiplay/(?P<room_name>\w+)/$', offmulticonsumers.GameConsumer.as_asgi()),
	# Offline tournament
#	re_path(r'ws/game/offline/tournament/(?P<room_name>\w+)/$', offtourconsumers.GameConsumer.as_asgi()),
	# Online 1 vs 1
	re_path(r'ws/game/online/oneversone/(?P<room_name>\w+)/$', ononeconsumers.GameConsumer.as_asgi()),
]
