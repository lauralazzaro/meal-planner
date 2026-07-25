up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f backend

test:
	docker compose exec backend pytest -v

lint:
	docker compose exec backend black --check .
	docker compose exec backend flake8 .

format:
	docker compose exec backend black .

shell:
	docker compose exec backend bash

migrate:
	docker compose exec backend alembic upgrade head

db-shell:
	docker compose exec db psql -U postgres -d mealplanner

SHELL := /bin/bash

dev:
	cd frontend && \
	source $$HOME/.nvm/nvm.sh && \
	nvm use && \
	npm run dev

install:
	cd frontend && \
	source $$HOME/.nvm/nvm.sh && \
	nvm use && \
	npm install

build:
	cd frontend && \
	source $$HOME/.nvm/nvm.sh && \
	nvm use && \
	npm run build