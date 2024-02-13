from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
	path('oauth/login/', views.oauth_login, name='oauth_login'),
	path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
	path('user/', views.get_user_info, name='user_profile')
]
