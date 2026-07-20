# Week 9 — Message brokers

Two things this week:

- **The lab** (`producer.py` + `consumer_group.py`) — see partitioning, consumer
  groups, per-key ordering, and rebalancing with your own eyes. *(Exercise 9)*
- **The capstone step** (`Jenkinsfile`) — your pipeline publishes one `ImagePushed`
  event to Kafka. *(the running capstone; consuming it comes later)*

## Files
| File | Purpose |
|------|---------|
| `docker-compose.yml` | single-broker Kafka (KRaft), container name `week9-kafka` |
| `requirements.txt` | Kafka Python client (`kafka-python-ng`) |
| `producer.py` | publish messages keyed by `order_id` across a 3-partition `orders` topic |
| `consumer_group.py` | a consumer in group `orders-workers`; run two to split partitions |
| `Jenkinsfile` | capstone: an **"Announce to Kafka"** stage that publishes `ImagePushed` |

---

## Lab — partitioning and consumer groups

```bash
# 1. Kafka + a 3-partition topic
docker compose -p week9 up -d
docker exec week9-kafka /opt/kafka/bin/kafka-topics.sh \
  --create --topic orders --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:9092

# 2. Python env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. produce keyed messages (prints the partition each order lands on)
python producer.py

# 4. run TWO consumers in the same group — separate terminals:
NAME=c1 python consumer_group.py
NAME=c2 python consumer_group.py
```

**Shortcut:** `./run_group.sh` starts both consumers at once (labeled `[c1]`/`[c2]`
in one terminal; Ctrl-C stops both). It also checks Kafka is up first. To see a
rebalance while it runs, in another terminal: `kill "$(cat .c1.pid)"`.
(You don't need to start the two at the same instant — Kafka rebalances whenever a
consumer joins or leaves; the script is just convenience.)

Watch: each consumer prints the partitions it was **assigned** (together they cover
all three, no overlap); re-run the producer and each message is handled by exactly
one consumer; every event for one `order_id` stays in order on a single consumer;
**kill one consumer** and the survivor **rebalances** to cover the freed partitions.

Tear down: `docker compose -p week9 down`.

---

## Capstone — the pipeline announces its build to Kafka

The `Jenkinsfile` adds an **"Announce to Kafka"** stage that publishes one
`ImagePushed` event to the `ci.images` topic after a build. It pipes the message
into the Kafka container's own console-producer via `docker exec` — **no Kafka
client in the agent, no shared-network setup**. Nothing consumes the event yet;
that comes in later weeks. Verify a send with:

```bash
docker exec week9-kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --topic ci.images --from-beginning --timeout-ms 6000 \
  --bootstrap-server localhost:9092
```

> **Validated** on macOS (Docker + Apache Kafka 3.9.0): keyed production pins each
> `order_id` to one partition; a two-member group splits the partitions and
> rebalances when one is killed; and the pipeline's `ImagePushed` send lands in
> `ci.images` and reads back cleanly.
