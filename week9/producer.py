"""Week 9 lab — produce keyed messages across a multi-partition topic.

Each message is KEYED by order_id, so all events for the same order land on the
same partition and stay in order, while different orders spread across the three
partitions. Watch the partition each message is sent to: a given key always maps
to the same partition.
"""
import json
import time

from kafka import KafkaProducer

BROKER = "localhost:9092"
TOPIC = "tickets"

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Several events per order_id, across a handful of orders, interleaved in time.
# These ids spread across all three partitions of a 3-partition topic.
events = [
    ("31", "opened"), ("32", "opened"), ("36", "opened"), ("35", "opened"),
    ("20", "opened"), ("21", "opened"), ("31", "assigned"), ("35", "assigned"),
    ("36", "assigned"), ("31", "resolved"), ("32", "assigned"), ("35", "resolved"),
    ("32", "resolved"), ("31", "closed"), ("35", "closed"), ("20", "assigned")
]

for ticket_id, status in events:
    event = {"ticket_id": ticket_id, "status": status}
    md = producer.send(TOPIC, key=ticket_id, value=event).get(timeout=10)
    print(f"ticket {ticket_id:<3} {status:<10} -> partition {md.partition} offset {md.offset}")
    time.sleep(0.3)

producer.flush()
producer.close()
print("done — notice every event for a given order_id landed on the same partition.")
