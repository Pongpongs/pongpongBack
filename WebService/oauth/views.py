from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from .models import UserProfile
import requests
from urllib.parse import urlencode
import os
from django.contrib import messages
from django.core.cache import cache
import redis
import json

# Create your views here.
def oauth_login(request):
	# GET 요청만 처리, 예기치 않은 요청 메소드는 거부
	if request.method != 'GET':
		return HttpResponseNotAllowed(['GET'])
	client_id = os.getenv('CLIENT_ID')
	params = {
		'client_id': client_id,
		'redirect_uri': 'https://localhost:8000/oauth/callback/',
        'response_type': 'code',
        'scope': 'public'  # Include scopes needed to access /v2/me
    }
	auth_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(params)}"
	return redirect(auth_url)

def get_authorization_code(request):
	return request.GET.get('code')

def get_access_token(code):
	client_id = os.getenv('CLIENT_ID')
	client_secret = os.getenv('CLIENT_SECRET')
	token_request_data = {
		'grant_type': 'authorization_code',
		'code': code,
		'client_id': client_id,
		'client_secret': client_secret,
		'redirect_uri': 'https://localhost:8000/oauth/callback/',
		'HTTP_REFERER': 'https://localhost:8000'
	}
	token_endpoint = 'https://api.intra.42.fr/oauth/token'
	try:
		response = requests.post(token_endpoint, data=token_request_data)
		if response.status_code == 200:
			token_data = response.json()
			return token_data.get('access_token'), None
		else:
			# Http Code = Status Code : 401, 403, 404, 422, 500
			# status_code에 대한 에러 처리
			http_code = response.status_code
	except requests.ConnectionError:
		# Http Code != Status Code : Connection refused, Reason : "Most likely cause is not using HTTPS"
		# 네트워크 연결 실패에 대한 에러 처리
		http_code = 500
	return None, http_code

def oauth_callback(request):
	# GET 요청만 처리, 예기치 않은 요청 메소드는 거부
	if request.method != 'GET':
		return HttpResponseNotAllowed(['GET'])
	authorization_code = get_authorization_code(request)
	if not authorization_code:
		# 접근 코드 발급 실패시 보일 화면
		return redirect('/access_code_erorr/')
	# 2FA 인증 위치
	access_token, status_code = get_access_token(authorization_code)
	if not access_token:
		# 토큰 발급 실패시 보일 화면
		error_message = f"Login failed with error code: {status_code}"
		messages.add_message(request, messages.ERROR, error_message)
		return redirect('/front/')
	# 토큰으로 유저 정보 획득
	user_info = get_user_info(access_token)
	# get_token_info(access_token) # 토큰 정보 추출
	# db에 유저 등록 (이미 있다면 스킵)
	registerUserinDB(user_info)
	# print_all_users() # db에 등록된 모든 유저 출력
	# 로그인 성공시 보일 첫 화면
	access_token_store_and_fetch(access_token)
	get_token_info_from_redis(access_token)
	return redirect('/index/')

def registerUserinDB(user_info):
	ids = user_info.get('id')
	login = user_info.get('login')
	email = user_info.get('email')
	userprofile, created = UserProfile.objects.get_or_create(
		ids=ids, 
		defaults={
		'ids': ids,
		'login': login,
		'email': email,
	})
	if not created:
		print(f'User {login} already exists')
	return None

def print_all_users():
	users = UserProfile.objects.all()
	for user in users:
		print(f'Nick: {user.login}, ids: {user.ids}, email: {user.email}')
	return None

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

# for test
def get_token_info(access_token):
	token_info_endpoint = 'https://api.intra.42.fr/oauth/token/info'
	headers = {
		'Authorization': f'Bearer {access_token}'
	}
	response = requests.get(token_info_endpoint, headers=headers)
	if response.status_code == 200:
		token_info = response.json()
		return token_info, None
	status_code = response.status_code
	return None, status_code

# redis test
def store_access_token(access_token):
	# store the access_token in the cache in 10 seconds
	cache.set('access_token', access_token, timeout=10)

def fetch_access_token():
	# fetch the access_token from the cache
	return cache.get('access_token')

def access_token_store_and_fetch(access_token):
	token_info = get_token_info(access_token)
	# token_info = ({key: value}, {key, value} ...) tuple
	# token_info[]
	json_data = json.dumps(token_info[0])
    # Connect to Redis
    # Adjust the connection parameters as necessary
	r = redis.Redis(host='localhost', port=6379, db=0)

    # Use the access_token as the key and the serialized JSON as the value
    # You might want to use a more specific key based on your application's needs
	r.set(access_token, json_data)

	print(f"Stored token info for access token: {access_token}")

def get_token_info_from_redis(access_token):
    # Connect to Redis
	r = redis.Redis(host='localhost', port=6379, db=0)

    # Retrieve the serialized JSON data by access_token
	json_data = r.get(access_token)
	
	if json_data:
		# Deserialize the JSON string back into a Python dictionary
		print(f"type of redis : {type(r)}") # redis.client.Redis
		print(f"type of token : {type(access_token)}") # str
		print(f"type of get(token)  : {type(json_data)}") # bytes
		data = json.loads(json_data)
		print(f"type of json : {type(data)}") # dict
		print("Data found")
		for key in data:
			print(f"{key} : {data[key]}")
		return data
	print(f"No data found for access token: {access_token}")
	return None
