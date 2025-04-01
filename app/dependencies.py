from redis.asyncio import Redis
from .kafka_utils import get_kafka_producer, get_kafka_consumer


def get_redis():
    return Redis(host="redis", port=6379)

def get_kafka_producer_dependency():
    return get_kafka_producer

def get_kafka_consumer_dependency():
    return get_kafka_consumer