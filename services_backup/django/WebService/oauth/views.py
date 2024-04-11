from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from .models import UserProfile
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import jwt
# from datetime import datetime, timedelta

# Create your views here.
@csrf_exempt
def realback(request):
	# POST 요청만 처리, 예기치 않은 요청 메소드는 거부
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST']) # 405 상태코드와 함께 어떤 메소드가 허용되는지(['POST']) 클라이언트에게 알려주는 용도
	token_header = request.headers.get('Authorization')
	if token_header is None:
		return HttpResponse('Unauthorized - Invalid Authorization header', status=401)
	token_scheme, token_value = token_header.split(' ')
	if token_scheme.lower() != 'bearer':
		return HttpResponse('Unauthorized - Invalid token scheme', status=401)
	data = decode_token(token_value)
	if data is None:
		return HttpResponse('Unauthorized - Decoding token error', status=401)
	user_email = data.get('user_email')
	access_token = data.get('access_token')
	user_info = get_user_info(access_token)
	if user_info is None:
		return HttpResponse('Unauthorized - Invalid access token', status=401)
	# 아래 이메일 대조 로직의 필요성?
	valid_email = user_info.get('email')
	if user_email != valid_email:
		return HttpResponse('Unauthorized - Email mismatch', status=401)
	# 로그인 성공, DB 등록
	registerUserinDB(valid_email)
	# db 등록된 이메일 확인
	print_new_user(valid_email)
	return HttpResponse('Ok', status=200)

def decode_token(token):
	secret_key = os.getenv('SECRET_KEY')
	decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
	return decoded_token

def get_user_info(access_token):
	user_info_endpoint = 'https://api.intra.42.fr/v2/me'
	headers = {
		'Authorization': f'Bearer {access_token}'
	}
	# "Authorization: Bearer YOUR_ACCESS_TOKEN" https://api.intra.42.fr/v2/me
	response = requests.get(user_info_endpoint, headers=headers)
	if response.status_code != 200:
        # 에러 처리
		print(f"Failed to retrieve user info. Status code: {response.status_code}, Response: {response.text}")
		return None
	user_info = response.json()
	return user_info

def registerUserinDB(valid_email):
	userprofile, created = UserProfile.objects.get_or_create(email=valid_email)
	if not created:
		print(f'User {valid_email} already exists')
	return None

def print_new_user(email):
	users = UserProfile.objects.all()
	for user in users:
		if user.email == email:
			print(f'email: {user.email}')
	return None

def print_all_users():
	users = UserProfile.objects.all()
	for user in users:
		print(f'Nick: {user.login}, ids: {user.ids}, email: {user.email}')
	return None
