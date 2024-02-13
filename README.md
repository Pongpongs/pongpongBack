# pongpongBack
webserver

진행상황
1. 테스트용 웹 서버 구현 (localhost)

2. 42서버 로그인 페이지를 사용해서 authorization_code 발급

3. authorization_code를 사용해서 access_token 발급

4. access_token을 사용해서 42 api (https://api.intra.42.fr/v2/me, 혹은 https://api.intra.42.fr/v2/users/{user}) 를 사용해서 유저 정보를 획득

진행중
1. 유저 정보를 db에 저장 (db와 비교후 없으면 신규 가입)

2. sqlite를 postgresql로 전환

3. access_token을 어떻게 저장하여 사용할지