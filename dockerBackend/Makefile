all:
	@docker compose -f ./docker-compose.yml --env-file ./.env up -d --build
down:
	@docker compose -f ./docker-compose.yml --env-file ./.env down

clean: down
	@docker system prune --all --force
	@docker volume prune --force

.PHONY: all down clean