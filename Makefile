PORT ?= 8000

install:
	poetry install

build:
	poetry build

package-install:
	python3 -m pip install --user dist/*.whl

uninstall:
	python3 -m pip uninstall --yes dist/*.whl

reinstall:
	pip install --user --force-reinstall dist/*.whl

dev:
	poetry run flask --app page_analyzer:app run

start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

selfcheck:
	poetry check

lint:
	poetry run flake8 page_analyzer