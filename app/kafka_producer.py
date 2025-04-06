from aiokafka import AIOKafkaProducer
import json
import asyncio

KAFKA_TOPIC = "search_topic"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

producer = None

async def init_kafka():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()

async def close_kafka():
    if producer:
        await producer.stop()

async def send_to_kafka(message):
    await init_kafka()
    try:
        value = json.dumps(message).encode("utf-8")
        await producer.send_and_wait(KAFKA_TOPIC, value)
    finally:
        await close_kafka()