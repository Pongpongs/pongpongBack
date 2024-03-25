from django.http import HttpResponseNotAllowed, HttpResponse
from .models import UserProfile
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
@csrf_exempt
def realback(request):
	# POST 요청만 처리, 예기치 않은 요청 메소드는 거부
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST'])
	data = json.loads(request.body)
	# 아래의 이메일 대조 방식을 다음과 같이 변경한다.
	# data.get으로 authorization_code 를 꺼내서 token을 발급한다.
	# token을 발급하고 token을 사용해 42api로 부터 email을 발급힌디.
	# email, 암호화한 토큰(추가 검증용)을 프론트로 보낸다.
	# 프론트에서 email을 사용해 2FA 인증을 한다.
	# 2FA인증이 끝나면 암호화한 토큰과 이메일을 프론트로 보낸다.
	# 복호화한 토큰을 사용해 42API로부터 이메일을 발급받아 이메일이 동일할 경우 db에 등록한다.
	useremail = data.get('userEmail')
	access_token = data.get('access_token')
	if not data:
		# response 에러
		return HttpResponse('Unauthorized', status=401)
	# 검증용 데이터 획득
	user_info = get_user_info(access_token)
	valid_email = user_info.get('email')
	# 유저 검증
	if useremail != valid_email:
		# 에러처리
		return HttpResponse('Unauthorized', status=401)
	# 로그인 성공, DB 등록
	registerUserinDB(user_info)
	print_all_users()
	return HttpResponse('Ok', status=200)

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
