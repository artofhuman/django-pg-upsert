DOCKER_COMPOSE := docker-compose -p django-pg-upsert
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm

DEFAULT: test

compose-up:
	${DOCKER_COMPOSE} up -d

compose-down:
	${DOCKER_COMPOSE} down

test:
	poetry run pytest

tox:
	tox

install:
	poetry install

lint:
	poetry run ruff check django_pg_upsert/ tests/
	poetry run ruff format --check django_pg_upsert/ tests/

fmt:
	poetry run ruff check --fix django_pg_upsert/ tests/
	poetry run ruff format django_pg_upsert/ tests/


publish:
	poetry publish --build
