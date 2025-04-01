from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers="kafka:9092",
                                value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    await producer.start()
    return producer

async def get_kafka_consumer():
    consumer = AIOKafkaConsumer(
        "response_topic",
        bootstrap_servers="kafka:9092",
        group_id="client_group",
        value_deserializer=lambda x:json.loads(x.decode('utf-8'))
    )
    await consumer.start()
    return consumer