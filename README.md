# MattShop

A dockerised django project representing an API for a simple shop, backed by a postgres database.

## How to use

Use the Makefile to set up a local development environment.`make bootstrap` is a good entry point, but all Makefile commands are detailed below. Requires an actively-running reasonably recent docker host.

### Makefile commands

* `make bootstrap` - Build the environment and run first-time database migrations.
* `make build` - a component of bootstrap. Rerun it when any python dependencies or dockerfiles change.
* `make run` - brings up services locally. When this completes, you should be able to hit the local API on the docker host (usually localhost) port 8000.
* `make shell` - launches an interactive django shell.
* `make migrate` - runs django migrations.
* `make django` - runs any `manage.py` command - add any additional commands by embedding in the DJANGO_CMD env var.
* `make test` - runs project unit tests.
* `make exec` - run a command on the container. Add the command itself in the CMD env var.
* `make load-fixture` - load some supplied fixture data for local testing.


### Endpoints

* `/healthcheck/heartbeat/` - An endpoint that always returns a 200.
* `/auth/login/` - Endpoint to acquire an auth token required for interacting with all subsequent endpoints.
* `/products/list/` - Endpoint to view a paginated list of products.
* `/order/create/` - Endpoint to create a new order.
* `/order/history/` - Endpoint to view a list of all previous orders made by a given requesting user.

### Some handy curl requests

#### Acquire an auth token

```
curl -XPOST localhost:8000/auth/login/ -d "{\"username\": \"matt\", \"password\": \"jackson\"}" --header "Content-Type: application/json"
```

#### Read product catalogue

```
curl -XGET localhost:8000/products/list/
```

#### Make an order

```
curl -XPUT localhost:8000/orders/create/ -d "{\"items\": [{\"product_id\": 6, \"quantity\": 1}]}" --header "Content-Type: application/json" --header "Authorization: Token 3aa905c8b99b518e889df6fc02ec80dca142054e"
```

#### View order history

```
curl -XGET localhost:8000/orders/history/ --header "Content-Type: application/json" --header "Authorization: Token 3aa905c8b99b518e889df6fc02ec80dca142054e"
```

## Technical Decisions

### Atomicity around order creation

This was done with django's `select_for_update()`, creating a row-level lock on all products when it comes to processing a given order. This would mean if a concurrent order request arrived for the same product while the first was still processing, the second process would hang waiting for the first transaction to commit before performing it's own row-level locks. In the worst-case, with very high contention over particular products, this could create a kind of queue of users waiting to check out particular products. If the wait-time were long-enough, HTTP requests could even time out.

This is one reason why the code within the atomic transaction block should execute as quickly as possible. There are some minor optimisations that could be made in what I produced here (some DB requests are repeated).

Another more-involved approach might be to "reserve stock" before a purchase, perhaps with a shopping basket system. When a user adds an item to a basket, the item then becomes unavailable to other customers until the customer either checks out (and the item becomes permanently unavailable), or the customer's basket times out after 5 or so minutes, and the products are added back to an availability pool. The disadvantage of this approach is it just moves the atomicity challenge to earlier in the sales process, vs outright removing it. An advantage of this approach is it decouples it from the order completion process, which might have a slower payment step connected to it.

Another simple but not total mitigation is storing stock in multiple pools that can be drawn from, perhaps a reflection of actual fulfilment centre stock levels. This would allow multiple users to concurrently purchase the same item, but the maximum concurrent users maxes out at the number of pools. A new challenge this introduces is how to deal with a customer ordering more stock than any single pool has.

## What I would do with more time

### Prices & Currencies

As it is, prices are just abstract numbers with no currency (or currency symbol) applied. A good next-step would be to extend the prices table to include a currency, and extend the `get_current_price` function to also query by desired currency.

### Swagger/OpenAPI spec

This would be nice, since it would open the door for autogenerating an API client, as well as being good documentation generally. Not hard to do either, but stopped due to time.

### Shopping basket

This would be a nice addition, allowing users to progressively "add items to basket", before "checking out" - creating an order on the whole basket. This would also open the door to "reserving items" for active baskets, which would go some way to providing a mitigation path for the high-traffic row-locking issue above.

### Payment

Some kind of notion of storing payment capabilities against a user and incorporating them into the order creation flow?

### Web server in docker-compose (e.g. nginx)

The docker-compose file just includes the application running in wsgi mode, and a postgres database. In reality, you would want to put it behind a real web server, such as nginx. It would be nice to put this in the developer environment too, to bring it as similar to production as is practicable. If you ever wanted to serve static content, this would also be a necessary step.

## Deployment notes

A dockerfile is included here, which opens the door for a number of possible deployment options. A key difference between local deployment and a production deployment is a separately configured PostgreSQL instance. However, this is provided by virtually all cloud providers. Two that I believe would be simple to deploy to would be Heroku or AWS Fargate (with RDS and a VPC with a public gateway). Both of these provide tools to build services from Docker containers. The steps you would need to follow are:

* Bring up a new PostgreSQL instance accessible only to your Heroku instance / VPC
* Configure environment variables for the application with all connection details to the new Postgres instance.
* Bring up the new application instance, ensuring it is able to reach the postgres instance. The docker image should automatically migrate the database and launch itself if it is able.
* Ensure the application instance is accessible on the public web - the heartbeat endpoint is a useful tool in this instance.
* This should be all that's required.
