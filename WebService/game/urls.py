from django.urls import path
from . import views

# SPA 프론트로 하단의 urlpatterns는 다 지울 예정
urlpatterns = [
	path('', views.index, name='index'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
	# offline
	path('off/2p/<str:room_name>/', views.off2proom, name='off2proom'),
	path('off/4p/<str:room_name>/', views.off4proom, name='off4proom'),
	path('off/tour/<str:room_name>/', views.offtourroom, name='offtourroom'),
	# online
	path('on/2p/<str:room_name>/', views.on2proom, name='on2proom'),
	path('on/4p/<str:room_name>/', views.on4proom, name='on4proom'),
	# path('on/tour/<str:room_name>/', views.ontourroom, name='ontourroom'),
]
