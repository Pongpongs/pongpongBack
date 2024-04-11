#!/bin/bash

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Migration initiating....."
# 작업 및 실행위치 변경
cd WebService

# Django 마이그레이션
python manage.py makemigrations
python manage.py migrate
echo "Migration done......"

# Django Daphne 서버 실행
daphne -b 0.0.0.0 -p 8000 WebService.asgi:application