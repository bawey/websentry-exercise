# Websentry (exercise project)

The project is a simple implementation of a website availability monitor (the producer) relaying its reports through a Kafka event bus where the reports are picked up by the consumer and persisted in a postgres database.

## Architecture overview

The [`producer`](./websentry/producer/__init__.py) package introduces a [`Sentry`](./websentry/producer/sentries.py) class tasked with checking the websites and producing instances of [`SiteReport`](./websentry/commons/sitereport.py). The latter are passed to a [`KafkaDispatcher`](./websentry/producer/dispatchers.py) instance that prepares the messages and sends them to the Kafka server.  
  
On the [receiving side](./websentry/consumer/__init__.py), the [`Consumer`](./websentry/consumer/consumer.py) fetches the messages that are subsequently persisted by a [`DBArchiver`](./websentry/consumer/archivers.py).  

In order to reduce the coupling between the classes, they are wired together by the relevant `main` methods of [`producer`](./websentry/producer/__init__.py) and 
[`consumer`](./websentry/consumer/__init__.py) packages respectively.

## Launching
Assuming that all the necessary [environment variables](#configuration-through-environment-variables) are set, the producer can be launched like so:
```bash
python -m websentry.producer
```
and the consumer like so:
```bash
python -m websentry.consumer
```
### Configuration through environment variables

The producer can be launched in a daemon-alike mode (with the `WEBSENTRY_INTERVAL` > 0) or can run on a one-off basis, allowing external utilities to control the frequency of launches (`cron`, `systemd`). It will fetch the websites designated by a comma-separated `WEBSENTRY_SITES` variable, optionally checking for the regular expression provided within the `WEBSENTRY_REGEXP` variable.  

Consumer can also work as a daemon (`WEBSENTRY_CONSUMER_ENABLE_DAEMON=1`), fetching the messages as soon as they are available; or be invoked on a one-off basis (`0`).
Among the others, the program needs a bunch of credentials/certificates to run, with the full sample configuration listed below:

```bash
export WEBSENTRY_KAFKA_CAFILE=/somedir/ca.pem
export WEBSENTRY_KAFKA_CERTFILE=/somedir/service.cert
export WEBSENTRY_KAFKA_KEY=/somedir/service.key
export WEBSENTRY_KAFKA_TOPIC=sitecheck
export WEBSENTRY_KAFKA_HOSTS=kafka-tomekbawej-2d43.aivencloud.com:19663
export WEBSENTRY_REGEXP='(?:id=")([^"]+)'
export WEBSENTRY_INTERVAL=30
export WEBSENTRY_SITES="https://google.com,http://something.that.does.not.exist,http://yahoo.com,https://icms.cern.ch/tools,http://google.com/404"   
export WEBSENTRY_CONSUMER_ENABLE_DAEMON=1
export WEBSENTRY_DATABASE_NAME=postgres
export WEBSENTRY_DATABASE_HOST=127.0.0.1
export WEBSENTRY_DATABASE_PORT=5432
export WEBSENTRY_DATABASE_USER=postgres
export WEBSENTRY_DATABASE_PASSWORD=docker
```

## DB Setup
The [`DBArchiver`](./websentry/consumer/archivers.py) class attempts to assume that responsibility by undertaking the necessary effort to recover from the `relation missing` DB error.
While the correctness of such approach is debatable (DB permissions), it reduces the fuss required to get things running.
Elsewhere (ie in the tests) the necessary procedures are in place as test fixtures.

## Testing
### Quick tests
These tests don't need any of the backend services to execute.
```bash
pytest test/fast
```
### Full tests 
In contrast to the quick tests, these require the Kafka and Postgres servers to be configured.  
The neecssary details can be worked out from the [`.github/workflows/ci.yaml`](./.github/workflows/ci.yaml) file and they involve a combination of credentials and certificate files, all fed into the applications through the corresponding [environment variables](#configuration-through-environment-variables).
```bash
pytest test
```
### CI (Github actions)
Please consult the [`.github/workflows/ci.yaml`](./.github/workflows/ci.yaml) file for details.