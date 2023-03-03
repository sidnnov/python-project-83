PORT ?= 8000

schema-load:
	psql page_analyzer < database.sql

db-create:
	createdb page_analyzer

db-reset:
	dropdb page_analyzer || true
	createdb page_analyzer

connect:
	psql -d page_analyzer

install:
	poetry install

build:
	poetry build

dev:
	poetry run flask --app page_analyzer:app --debug run

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

selfcheck:
	poetry check

lint:
	poetry run flake8 page_analyzer

pytest:
	poetry run pytest

check: selfcheck pytest lint

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml