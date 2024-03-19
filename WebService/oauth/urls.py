from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
	path('realback/send', views.realback, name='realback'),
]
