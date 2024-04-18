# MattShop

A dockerised django project representing an API for a simple shop, backed by a postgres database.

## How to use

### Makefile commands

* `make bootstrap` - Build the environment and run first-time database migrations.
* `make build` - a component of bootstrap. Rerun it when any python dependencies or dockerfiles change.
* `make run` - brings up services locally. When this completes, you should be able to hit the local API on the docker host (usually localhost) port 8000.
* `make shell` - launches an interactive django shell.
* `make migrate` - runs django migrations.
* `make django` - runs any `manage.py` command - add any additional commands by embedding in the DJANGO_CMD env var.
* `make test` - runs project unit tests.
* `make exec` - run a command on the container. Add the command itself in the CMD env var.


### Endpoints

* `/healthcheck/heartbeat/` - An endpoint that always returns a 200.
* `/login` - Endpoint to acquire an auth token required for interacting with all subsequent endpoints.

## Technical Decisions
