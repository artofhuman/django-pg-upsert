DOCKER_COMPOSE := docker-compose -p django-pg-upsert
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm

DEFAULT: test

compose-up:
	${DOCKER_COMPOSE} up -d

compose-down:
	${DOCKER_COMPOSE} down

test:
	pytest

install:
	poetry install

lint:
	flake8 django_pg_upsert/
