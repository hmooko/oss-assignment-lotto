PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/python -m pip

.PHONY: install test check docker-build docker-up docker-down docker-test docker-health create-round verify

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) manage.py test

check:
	$(PYTHON) manage.py makemigrations --check --dry-run

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-test:
	docker compose exec web python manage.py test

docker-health:
	curl -I http://localhost:8000

create-round:
	docker compose exec web python manage.py create_next_round

verify: check test docker-build docker-up docker-test docker-health
