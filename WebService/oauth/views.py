from django.http import HttpResponseNotAllowed, HttpResponse, JsonResponse
from .models import UserProfile
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import jwt
from datetime import datetime, timedelta

# Create your views here.
@csrf_exempt
def realback(request):
	# POST 요청만 처리, 예기치 않은 요청 메소드는 거부
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST']) # 405 상태코드와 함께 어떤 메소드가 허용되는지(['POST']) 클라이언트에게 알려주는 용도
	token_header = request.headers.get('Authorization')
	if token_header is None:
		return HttpResponse('Unauthorized data error', status=401)
	token_scheme, token_value = token_header.split(' ')
	data = decode_token(token_value)
	user_email = data.get('user_email')
	access_token = data.get('access_token')
	user_info = get_user_info(access_token)
	if user_info is None:
		return HttpResponse('Unauthorized access token', status=401)
	valid_email = user_info.get('email')
	if user_email != valid_email:
		return HttpResponse('Unauthorized email', status=401)
	# 로그인 성공, DB 등록
	registerUserinDB(valid_email)
	# db 등록된 이메일 확인
	print_new_user(valid_email)
	return HttpResponse('Ok', status=200)

# def encode_token(email):
# 	secret_key = os.getenv('SECRET_KEY')
# 	payload = {
# 		'email': email,
# 		'exp': datetime.utcnow() + timedelta(seconds=60)
# 	}
# 	encoded_token = jwt.encode(payload, secret_key, algorithm='HS256')
# 	return encoded_token

def decode_token(token):
	secret_key = os.getenv('SECRET_KEY')
	decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
	return decoded_token

# def get_access_token(code):
# 	client_id = os.getenv('CLIENT_ID')
# 	client_secret = os.getenv('CLIENT_SECRET')
# 	token_request_data = {
# 		'grant_type': 'authorization_code',
# 		'code': code,
# 		'client_id': client_id,
# 		'client_secret': client_secret,
# 		'redirect_uri': 'https://pongpongback.duckdns.org/realback/send/',
# 		'HTTP_REFERER': 'https://localhost:8000'
# 	}
# 	token_endpoint = 'https://api.intra.42.fr/oauth/token'
# 	try:
# 		response = requests.get(token_endpoint, data=token_request_data)
# 		if response.status_code == 200:
# 			token_data = response.json()
# 			return token_data.get('access_token'), None
# 		else:
# 			http_code = response.status_code
# 	except requests.ConnectionError:
# 		http_code = 500
# 	return None, http_code

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
