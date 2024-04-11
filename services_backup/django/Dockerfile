FROM python:3.10

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
RUN pip install django daphne channels requests channels_redis psycopg2-binary whitenoise websockets PyJWT

# 프로젝트 파일 복사
COPY ./WebService ./WebService

# 시작 스크립트 복사
COPY ./tools/start.sh ./tools/start.sh
RUN chmod +x ./tools/start.sh
# COPY ./tools/.env ./tools/.env

# 시작 명령
# Dockerfile 외부의 폴더에는 접근할 수 없기 때문에 django 전용의 tools 폴더를 사용함
CMD ["./tools/start.sh"]