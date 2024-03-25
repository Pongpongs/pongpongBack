from django.urls import path
from . import views

# SPA 프론트로 하단의 urlpatterns는 다 지울 예정
urlpatterns = [
	path('', views.index, name='index'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
	# offline
	path('off/2p/<str:room_name>/', views.offoneroom, name='offoneroom'),
	path('off/4p/<str:room_name>/', views.offmultiroom, name='offmultiroom'),
	path('off/tour/<str:room_name>/', views.offtourroom, name='offtourroom'),
	# online
	path('on/2p/<str:room_name>/', views.ononeroom, name='ononeroom'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
]
