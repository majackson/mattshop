bootstrap:
	make build && make migrate && make django DJANGO_CMD=create_user

build:
	docker compose build

django:
	docker compose run --rm api bash -c "poetry run ./manage.py ${DJANGO_CMD}"

exec:
	docker compose run --rm api bash -c "${CMD}"

shell:
	DJANGO_CMD=shell make django

migrate:
	DJANGO_CMD=migrate make django

load-fixture:
	DJANGO_CMD="loaddata fixture.json" make django

run:
	docker compose up

test:
	docker compose run --rm api bash -c 'poetry run pytest -c tests/pytest.ini --strict $${TEST_ARGS:-"tests/"}'


