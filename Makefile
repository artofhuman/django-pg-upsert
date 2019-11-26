DOCKER_COMPOSE := docker-compose -p django-pg-upsert
DOCKER_COMPOSE_RUN := $(DOCKER_COMPOSE) run --rm

DEFAULT: test

compose-up:
	${DOCKER_COMPOSE} up

compose-down:
	${DOCKER_COMPOSE} down

test:
	pytest

install:
	poetry install

bash:
	${DOCKER_COMPOSE_RUN} app bash
