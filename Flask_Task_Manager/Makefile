APP_SERVICE = dev-db 

COMPOSE = docker compose 

migrate:
	$(COMPOSE) exec $(APP_SERVICE) flask db upgrade 

revision:
	$(COMPOSE) exec $(APP_SERVICE)  uv run flask --app run.py db migrate -m "$(msg)"

shell:
	$(COMPOSE) exec $(APP_SERVICE) sh

reset:
	$(COMPOSE) down -v 
