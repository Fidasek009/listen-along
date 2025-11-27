.PHONY: help build up down logs clean

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build containers
	docker compose build

up: ## Start containers
	docker compose up -d

down: ## Stop containers
	docker compose down

logs: ## Show backend logs
	docker compose logs -f backend

clean: ## Remove containers and volumes
	docker compose down -v --rmi local
