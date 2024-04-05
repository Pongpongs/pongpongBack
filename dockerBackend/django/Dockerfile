FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
RUN apt-get update && apt-get install -y redis-server postgresql postgresql-contrib && rm -rf /var/lib/apt/lists/*
RUN pip install django daphne channels requests channels_redis psycopg2-binary whitenoise websockets PyJWT

# 프로젝트 파일 복사
COPY ../../webService ./WebService

# 시작 스크립트 복사
COPY ../../start.sh /start.sh
RUN chmod +x /start.sh

# 시작 명령
CMD ["/start.sh"]