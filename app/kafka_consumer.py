from aiokafka import AIOKafkaConsumer
import json
import asyncio

KAFKA_TOPIC = "response_topic"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

consumer = None

async def init_kafka():
    global consumer
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="client_group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )
    await consumer.start()

async def close_kafka():
    if consumer:
        await consumer.stop()

async def consume_response(request_id):
    await init_kafka()
    try:
        async for msg in consumer:
            if msg.value.get("request_id") == request_id:
                return msg.value.get("results")
    finally:
        await close_kafka()