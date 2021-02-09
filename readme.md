# Websentry (exercise project)

The project is a simple implementation of a website availability monitor (the producer) relaying its reports through a Kafka event bus where the reports are picked up by the consumer and persisted in a postgres database.

## Launching
```python
python -m websentry.producer
```
or 
```python
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
The `DBArchiver` class attempts to assume that responsibility by undertaking the necessary effort to recover from the `relation missing` DB error.
While the correctness of such approach is debatable (DB permissions), it reduces the fuss required to get things running.
Elsewhere (ie in the tests) the necessary procedures are in place as test fixtures.

## Testing
### Launch quick tests
```bash
pytest test/fast
```
### Launch full tests (reqires working connection to services)
Running those requires configuring the necessary services (Kafka, Postgres) - similarly to how it's done in CI.
```bash
pytest test
```
### CI
Please consult the `.github/workflows` file for more details.