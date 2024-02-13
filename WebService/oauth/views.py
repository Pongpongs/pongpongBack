from django.shortcuts import redirect
from . import models
import requests
from urllib.parse import urlencode

# Create your views here.
def oauth_login(request):
	params = {
		'client_id': 'u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1',
        'redirect_uri': 'http://localhost:8000/oauth/callback/',
        'response_type': 'code',
        'scope': 'public'  # Include scopes needed to access /v2/me
    }
    # Construct the authorization URL
	auth_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(params)}"
    # Redirect the user to the authorization server
	return redirect(auth_url)

def get_access_token(code):
	token_request_data = {
		'grant_type': 'authorization_code',
		'code': code,
		'client_id': 'u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1',
		'client_secret': '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',
		'redirect_uri': 'http://localhost:8000/oauth/callback/'
	}
	# token의 엔드 포인트 (데이터 교환 장소)
	token_endpoint = 'https://api.intra.42.fr/oauth/token'
	# access_token을 발급받기 위해 token_request_data로 42서버에서 검증을 거침
	response = requests.post(token_endpoint, data=token_request_data)
	token_data = response.json()
	return token_data.get('access_token')

def oauth_callback(request):
	# 접근 코드 발급
	access_code = request.GET.get('code')
	if access_code:
		# 2FA 인증 위치
		# 
		# 접근 토큰 발급
		access_token = get_access_token(access_code)
		if access_token:
			# 접근 토큰을 사용해서 유저 프로필 추출
			# 유저 프로필을 분해해서 유저 id, 정보 추출후 db와 대조
			# db에 없으면 db에 등록
			# create user in db
			# user = models.UserAccessToken
			# user.user_profile = "tmp_user"
			# user.token = access_token
			# print(access_token)
			print('token info\n')
			get_token_info(access_token)
			registerUserinDB(access_token)
			return redirect('/index/') # 로그인 성공시 보일 첫 화면
		return redirect('/token_error/') # 토큰 발급 실패시 보일 화면
	return redirect('/access_code_erorr/') # 접근 코드 발급 실패시 보일 화면

def registerUserinDB(access_token):
	# extract user_info with access_token
	# parsing specific info from userinfo
	# compare userinfo with database's userinfo
	# if already in the database
	# return nothing
	# else
	# then register
	user_info = get_user_info(access_token)
	print(user_info.get('id'))
	print(user_info.get('login'))
	print(user_info.get('first_name'))
	print(user_info.get('last_name'))
	print(user_info.get('usual_full_name'))
	return None

def get_user_personal_info(access_token):
	user_info_endpoint = 'https://api.intra.42.fr/v2/users/jeongmil'
	headers = {
		'Authorization': f'Bearer {access_token}'
	}
	response = requests.get(user_info_endpoint, headers=headers)
	if response.status_code == 200:
		user_info = response.json()
		return user_info
	else:
		print(f"Failed to retrieve user info. Status code: {response.status_code}")
		return None

def get_user_info(access_token):
    # The endpoint for the user profile information
	user_info_endpoint = 'https://api.intra.42.fr/v2/me'
	# Include the access token in the Authorization header
	headers = {
		'Authorization': f'Bearer {access_token}'
	}
	# Make the GET request to the user info endpoint
	response = requests.get(user_info_endpoint, headers=headers)
	# Check if the request was successful
	if response.status_code == 200:
        # The request was successful, parse and return the user information
		user_info = response.json()
		return user_info
	else:
        # Handle error responses appropriately
		print(f"Failed to retrieve user info. Status code: {response.status_code}, Response: {response.text}")
		return None

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

# for test
def get_achiev_info(access_token):
	achiev_info_endpoint = 'https://api.intra.42.fr/v2/achievements'

	headers = {
		'Authorization': f'Bearer {access_token}'
	}
	response = requests.get(achiev_info_endpoint, headers=headers)
	if response.status_code == 200:
		token_info = response.json()
		return print(token_info)
	else:
		return print(f"Invalid Token. Status code: {response.status_code}, Response: {response.text}")

# 백엔드 목표
# 유저 데이터에서 필요한 정보만 파싱해서 db에 저장 (토큰은 저장하면 안 됨!!)

# backup
# def oauth_login(request):
# 	# params = {
# 	# 	'client_id': 'u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1',
#     #     'redirect_uri': 'http://localhost:8000/oauth/callback/',
#     #     'response_type': 'code',
#     #     'scope': 'public'  # Include scopes needed to access /v2/me
#     # }
#     # # Construct the authorization URL
# 	# auth_url = f"https://api.intra.42.fr/oauth/authorize?{urlencode(params)}"
#     # # Redirect the user to the authorization server
# 	# return redirect(auth_url)
# 	auth_url = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Foauth%2Fcallback%2F&response_type=code'
# 	return redirect(auth_url)

# def get_access_token(code):
# 	token_request_data = {
# 		'grant_type': 'client_credentials',
# 		'code': code,
# 		'client_id': 'u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1',
# 		'client_secret': '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',
# 	}
# 	# bellow not working at this time
# 	# token_request_data = {
# 	# 	'grant_type': 'authorization_code',
# 	# 	'code': code,
# 	# 	'client_id': 'u-s4t2ud-12a8b2c44b3826f8b6d69f201be6df88df1fd800042d274025450ca2d74739a1',
# 	# 	'client_secret': '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',
# 	# 	'redirect_uri': 'http://localhost:8000/oauth/callback/' # uri 끝에 '/'를 안 붙여서 토큰 생성 오류가 난 것
# 	# }
# 	# token의 엔드 포인트 (데이터 교환 장소)
# 	token_endpoint = 'https://api.intra.42.fr/oauth/token'
# 	# access_token을 발급받기 위해 token_request_data로 42서버에서 검증을 거침
# 	response = requests.post(token_endpoint, data=token_request_data)
# 	token_data = response.json()
# 	return token_data.get('access_token')
	

	#include <string>
#include <vector>
