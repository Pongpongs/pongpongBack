from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
	# 람다식은 삭제 예정
	path('index/', views.index_view, name='index_view'),
	path('posts/', views.post_view, name='post_view'),
	path('posts/add/', views.add_post, name='add_post_view'),
	path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post')
]
