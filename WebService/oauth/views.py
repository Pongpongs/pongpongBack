from django.shortcuts import redirect
from .models import UserProfile
import requests
from urllib.parse import urlencode
import os

# Create your views here.
def oauth_login(request):
	client_id = os.getenv('CLIENT_ID')
	params = {
		'client_id': client_id,
		'redirect_uri': 'https://localhost:8000/oauth/callback/',
        'response_type': 'code',
        'scope': 'public'  # Include scopes needed to access /v2/me
    }
    # Construct the authorization URL
	auth_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(params)}"
    # Redirect the user to the authorization server
	return redirect(auth_url)

def get_access_token(code):
	client_id = os.getenv('CLIENT_ID')
	client_secret = os.getenv('CLIENT_SECRET')
	token_request_data = {
		'grant_type': 'authorization_code',
		'code': code,
		'client_id': client_id,
		'client_secret': client_secret,
		'redirect_uri': 'https://localhost:8000/oauth/callback/'
	}
	# token의 엔드 포인트 (데이터 교환 장소)
	token_endpoint = 'https://api.intra.42.fr/oauth/token'
	# access_token을 발급받기 위해 token_request_data로 42서버에서 검증을 거침
	response = requests.post(token_endpoint, data=token_request_data)
	token_data = response.json()
	return token_data.get('access_token')

def oauth_callback(request):
	access_code = request.GET.get('code')
	if not access_code:
		# 접근 코드 발급 실패시 보일 화면
		return redirect('/access_code_erorr/')
	# 2FA 인증 위치
	access_token = get_access_token(access_code)
	if not access_token:
		# 토큰 발급 실패시 보일 화면
		return redirect('/token_error/')	
	# 토큰으로 유저 정보 획득
	user_info = get_user_info(access_token)
	# get_token_info(access_token) # 토큰 정보 추출
	registerUserinDB(user_info) # db에 유저 등록 (이미 있다면 스킵)
	# print_all_users() # db에 등록된 모든 유저 출력
	return redirect('/index/') # 로그인 성공시 보일 첫 화면

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
		return print(token_info)
	else:
		return print(f"Invalid Token. Status code: {response.status_code}, Response: {response.text}")
