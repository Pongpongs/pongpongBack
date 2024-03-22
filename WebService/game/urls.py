from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
	# offline
	path('offline/oneversone/<str:room_name>/', views.offoneroom, name='offoneroom'),
	path('offline/multiplay/<str:room_name>/', views.offmultiroom, name='offmultiroom'),
	path('offline/tournament/<str:room_name>/', views.offtourroom, name='offtourroom'),
	# online
	path('online/oneversone/<str:room_name>/', views.ononeroom, name='ononeroom'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
	# path('<str:online_status>/<str:game_mode>/<str:room_name>/', views.room, name='room'),
]
