# @ : make가 해당 명령줄을 실행한다는 내용이 터미널에 나오지 않게 함, echo의 경우 echo 내용만 출력됨
# mkdir -p : 에러 출력 방지
all:
	@docker compose -f ./docker-compose.yml --env-file ./.env up -d --build

down:
	@docker compose -f ./docker-compose.yml --env-file ./.env down

clean:
	@echo "Cleaning up"
	@docker compose -f ./docker-compose.yml --env-file ./.env down
	@docker system prune --all
	@docker volume prune --all
	@docker network prune

fclean:
	@echo "Forcefully cleaning up"
	@docker compose -f ./docker-compose.yml --env-file ./.env down
	@docker system prune --all --force
	@docker volume prune --all --force
	@docker network prune --force

.PHONY: all down clean fclean