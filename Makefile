.PHONY: help build up down restart logs shell db-shell test clean seed

help:
	@echo "Blog CMS - Available Commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Open Flask shell"
	@echo "  make db-shell    - Open PostgreSQL shell"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make seed        - Seed database with initial data"
	@echo "  make migrate     - Run database migrations"
	@echo "  make admin       - Create admin user"

build:
	docker compose build

up:
	docker compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Services started! Access the blog at http://localhost"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

shell:
	docker compose exec flask flask shell

db-shell:
	docker compose exec postgres psql -U bloguser -d blogdb

test:
	docker compose exec flask pytest tests/ -v

clean:
	docker compose down -v
	@echo "Cleaned up containers and volumes"

seed:
	docker compose exec flask flask seed-db

migrate:
	docker compose exec flask flask db upgrade

admin:
	@read -p "Enter admin email: " email; \
	read -sp "Enter admin password: " password; \
	echo ""; \
	docker compose exec flask flask create-admin --email $$email --password $$password

init: build up migrate seed
	@echo "Blog CMS initialized successfully!"
	@echo "Access the blog at http://localhost"
	@echo "Admin credentials: admin@blog.com / admin123"