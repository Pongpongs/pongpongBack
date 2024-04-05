#!/bin/bash

# Redis 서버 시작
redis-server --daemonize yes

# PostgreSQL 서버 시작
service postgresql start

# env 파일 적용
source .env
# export POSTGRES_USER=root
# export POSTGRES_PASS=pong
# export DB_NAME=pongpongdb

# PostgreSQL 사용자 및 데이터베이스 설정
# 실제 사용 환경에 맞게 POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB를 변경해주세요.
su - postgres -c "psql -c \"CREATE DATABASE $DB_NAME;\""
su - postgres -c "psql -c \"CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASS';\""
su - postgres -c "psql -c \"ALTER ROLE $POSTGRES_USER SET client_encoding TO 'utf8';\""
su - postgres -c "psql -c \"ALTER ROLE $POSTGRES_USER SET default_transaction_isolation TO 'read committed';\""
su - postgres -c "psql -c \"ALTER ROLE $POSTGRES_USER SET timezone TO 'Asia/Seoul';\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $POSTGRES_USER;\""
# 아래는 db 권한 문제로 마이그레이션에 실패하는 문제가 발생해 추가한 코드 
su - postgres -c "psql -c \"ALTER DATABASE $DB_NAME OWNER TO $POSTGRES_USER;\""

# 작업 및 실행위치 변경
cd WebService

# Django 마이그레이션
python manage.py makemigrations
python manage.py migrate

# Django Daphne 서버 실행
daphne -b 0.0.0.0 -p 8000 WebService.asgi:application