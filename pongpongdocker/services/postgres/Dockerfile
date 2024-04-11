FROM postgres:latest

# 초기화 스크립트 : 마이그레이션을 위한 db 생성, 권한 설정
COPY ./tools/init.sh /docker-entrypoint-initdb.d/init.db.sh

EXPOSE 5432

# PostgreSQL 이미지는 자체 ENTRYPOINT와 CMD를 가지고 있으므로 추가적인 ENTRYPOINT 또는 CMD를 설정할 필요 없음