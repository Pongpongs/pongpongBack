실행 방법

0. git clone
git clone (git_name)

1. venv 재설치
cd pongpongBack

rm -rf myprojectvenv

python3 -m venv myprojectvenv

2. venv 실행
. myprojectvenv/bin/activate

3. modules 설치
pip install -r requirements.txt
(설치중 에러가 발생할 수 있지만 무시해도 됨)

4. server 실행
cd WebService

bash execute_server.sh

5. optional
서버 작동 확인
cat nohup.out
- 서버 실행 로그 확인
- 각종 에러 메서지가 있다면 서버 실행에 문제가 있다는 것

ps -ef | grep daphne
- 작동중인 프로세스에서 서버가 있는지 확인
아래와 같이 로그가 뜨면 성공
ubuntu      1195       1  1 06:25 pts/0    00:00:08 /usr/bin/python3 /home/ubuntu/.local/bin/daphne -e ssl:8000:privateKey=/etc/letsencrypt/live/pongpongback.duckdns.org/fullchain.pem:certKey=/etc/letsencrypt/live/pongpongback.duckdns.org/privkey.pem WebService.asgi:application
ubuntu      1416    1124  0 06:36 pts/0    00:00:00 grep --color=auto daphne
아래 로그만 있다면 실패
ubuntu      1416    1124  0 06:36 pts/0    00:00:00 grep --color=auto daphne

pkill -f daphne
- 서버 정지

