# Week 9 — Capstone step 1: the pipeline announces its build to Kafka

The running capstone starts here. This week the only new capstone piece is the
**send**: after your pipeline builds an image, it publishes one `ImagePushed`
event to a Kafka topic. Consuming and reacting to that event comes in later weeks.

## Files
| File | Purpose |
|------|---------|
| `docker-compose.yml` | single-broker Kafka (KRaft), container name `week9-kafka` |
| `Jenkinsfile` | adds an **"Announce to Kafka"** stage that publishes `ImagePushed` |

## Why it's this simple
The `Announce to Kafka` stage pipes a message into the Kafka container's own
console-producer via `docker exec`, using the Docker socket the agent already
mounts (as in earlier weeks). So there's **no Kafka client to install in the
agent and no shared-network setup** — that complexity is deferred until the
consumer side needs it.

## Run it
```bash
# 1. bring up Kafka and create the topic
docker compose -p week9 up -d
docker exec week9-kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic ci.images --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:9092

# 2. run your pipeline (the Jenkinsfile 'Announce to Kafka' stage publishes the event).
#    The agent needs the Docker socket mounted and the week9-kafka container running —
#    the same setup you've used since the earlier Jenkins weeks.

# 3. confirm the message landed
docker exec week9-kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic ci.images --from-beginning --timeout-ms 6000 \
  --bootstrap-server localhost:9092
```

You should see one `ImagePushed` event per build, e.g.:
```json
{"event":"ImagePushed","image":"calculator","tag":"1","branch":"main"}
```

Tear down: `docker compose -p week9 down`.

> **Validated** on macOS (Docker + Apache Kafka 3.9.0): the pipeline's send lands
> in `ci.images` and reads back cleanly. The partitioning / consumer-group /
> rebalance material (the full event-driven CI story) builds on top of this in the
> weeks that follow.
