# MattShop

A dockerised django project representing an API for a simple shop, backed by a postgres database.

## How to use

Use the Makefile to set up a local development environment. All Makefile commands are detailed below. Requires an actively-running reasonably recent docker host.

`make bootstrap` is a good entry point, following this you may want to run `make load-fixture` to quickly get some test data, then `make run` to bring the server up and start querying endpoints.

### All Makefile commands

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
* `/auth/login/` - Endpoint to acquire an auth token required for interacting with all subsequent endpoints. This endpoints takes a POST request with a JSON-encoded body containing "username" and "password" fields.
* `/products/list/` - Endpoint to view a paginated list of products. This endpoint is accessible via GET, and requires no authentication token.
* `/order/create/` - Endpoint to create a new order. This endpoint requires an authentication token provided by the "Authorization" header. It is accessible via a PUT request, with a JSON-encoded body. The JSON provided should follow the structure structure: `{'items': [{'product_id': 12, 'quantity': 1}, {'product_id': 13, 'quantity': 2}]}`. Within the `items` key, multiple products can be on a single order.
* `/order/history/` - Endpoint to view a list of all previous orders made by a given requesting user. This endpoint is accessible via GET, and requires no further parameters. It requires an authentication token provided in the "Authorization" HTTP header.

### Some handy curl requests

#### Acquire an auth token

```
curl -XPOST localhost:8000/auth/login/ -d "{\"username\": \"megangates\", \"password\": \"\!4UWkNLxt*\"}" --header "Content-Type: application/json"
```

#### Read product catalogue

```
curl -XGET localhost:8000/products/list/
```

#### Make an order

```
curl -XPUT localhost:8000/orders/create/ -d "{\"items\": [{\"product_id\": 6, \"quantity\": 1}]}" --header "Content-Type: application/json" --header "Authorization: Token 3aa905c8b99b518e889df6fc02ec80dca142054f"
```

#### View order history

```
curl -XGET localhost:8000/orders/history/ --header "Content-Type: application/json" --header "Authorization: Token 3aa905c8b99b518e889df6fc02ec80dca142054f"
```

## Technical Decisions

### Atomicity around order creation

This was done with django's `select_for_update()`, creating a row-level lock on all products when it comes to processing a given order. This would mean if a concurrent order request arrived for the same product while the first was still processing, the second process would hang waiting for the first transaction to commit before performing it's own row-level locks. In the worst-case, with very high contention over particular products, this could create a kind of queue of users waiting to check out particular products. If the wait-time were long-enough, HTTP requests could even time out.

This is one reason why the code within the atomic transaction block should execute as quickly as possible. There are some minor optimisations that could be made in what I produced here (some DB requests are repeated).

Another more-involved approach might be to "reserve stock" before a purchase, perhaps with a shopping basket system. When a user adds an item to a basket, the item then becomes unavailable to other customers until the customer either checks out (and the item becomes permanently unavailable), or the customer's basket times out after 5 or so minutes, and the products are added back to an availability pool. The disadvantage of this approach is it just moves the atomicity challenge to earlier in the sales process, vs outright removing it. An advantage of this approach is it decouples it from the order completion process, which might have a slower payment step connected to it.

Another simple but not total mitigation is storing stock in multiple pools that can be drawn from, perhaps a reflection of actual fulfilment centre stock levels. This would allow multiple users to concurrently purchase the same item, but the maximum concurrent users maxes out at the number of pools. A new challenge this introduces is how to deal with a customer ordering more stock than any single pool has.

### Multiple prices against each product

Prices are not simply stored on the Product table, and instead a ProductPrice table is FK'd to the Product table. The reason for this is that it may be useful to have a record of historical price for a given product, which may be important to allow for retrospectively auditing what was charged to customers and when. Additionally, if the application were to be extended to support multiple currencies, an indexed "currency" column could be added to this table, in order to allow for storing multiple active prices (across different currencies) against a single product.

### Prices redundantly stored on Orders and OrderItems

In addition to storing multiple prices against products, prices are also redundantly stored on the OrderItem record, and additionally an "order total" is stored on the Order record. There are a few reasons for this:
* The order total represents the actual amount that might be charged to a user. It's important for accountancy reasons to have an indisputable record of this at the time of order creation. The alternative would be to query for a historical price in the Product/ProductPrice models. In the event of a historical pricing dispute with a customer, it may be necessary to jump through some hoops to understand _why_ a total price is as it was saved here. But additional tooling could potentially help with this.
* Shipping costs could potentially be added - this would make the total price not simply the sum of all the OrderItems * quantity.
* If the application were to be extended to support some form of discount coding, the price charged per-item and in total might differ from the simple historical price. Another example of this is bulk-discounting when meeting certain quantity thresholds.

## What I would do with more time

### Prices & Currencies

As it is, prices are just abstract numbers with no currency (or currency symbol) applied. A good next-step would be to extend the prices table to include a currency, and extend the `get_current_price` function to also query by desired currency.

### Swagger/OpenAPI spec

This would be nice, since it would open the door for autogenerating an API client, as well as being good documentation generally. Not hard to do either, but stopped due to time.

### Shopping basket

This would be a nice addition, allowing users to progressively "add items to basket", before "checking out" - creating an order on the whole basket. This would also open the door to "reserving items" for active baskets, which would go some way to providing a mitigation path for the high-traffic row-locking issue above.

### Payment & additional user fields

An obvious additional need for this project would be delivery and payment details for a given user. Each of these could have multiple per user, so it makes to use a new of table for each of these, and FK them to the User model (many-to-one).

### Web server in docker-compose (e.g. nginx)

The docker-compose file just includes the application running in wsgi mode, and a postgres database. In reality, you would want to put it behind a real web server, such as nginx. It would be nice to put this in the developer environment too, to bring it as similar to production as is practicable. If you ever wanted to serve static content, this would also be a necessary step.

### Usage of UUIDs instead of autoincrementing primary keys

Django's default is to use autoincrementing primary keys for all objects. This is usually fine for small projects, but it can be sensible to use UUID keys instead. These have the advantages:
* autoincrementing IDs can leak to users the rough number (or scale of) products, users, or orders. This information could be business-sensitive. UUIDs are opaque in this regard.
* UUIDs have the distributed scaling advantage that they can be generated across multiple services with a high confidence that no key will ever clash, without any need for synchronising.

It would be fairly simple to extend this project to use UUID keys at this stage. However, it would mean regenerating and re-storing all fixtures.

## Deployment notes

A dockerfile is included here, which opens the door for a number of possible deployment options. A key difference between local deployment and a production deployment is a separately configured PostgreSQL instance. However, this is provided by virtually all cloud providers. Two that I believe would be simple to deploy to would be Heroku or AWS Fargate (with RDS and a VPC with a public gateway). Both of these provide tools to build services from Docker containers. The steps you would need to follow are:

* Bring up a new PostgreSQL instance accessible only to your Heroku instance / VPC
* Configure environment variables for the application with all connection details to the new Postgres instance.
* Bring up the new application instance, ensuring it is able to reach the postgres instance. The docker image should automatically migrate the database and launch itself if it is able.
* Ensure the application instance is accessible on the public web - the heartbeat endpoint is a useful tool in this instance.
* This should be all that's required.
