from fastapi import FastAPI, Depends, HTTPException
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer 
import redis.asyncio as redis 
import json 
from uuid import uuid4 

app = FastAPI()

# Конфигурация 
KAFKA_BROKERS = "kafka:9092" 
REQUEST_TOPIC = "search_topic" 
RESPONSE_TOPIC = "response_topic" 
redis_client = redis.Redis(host="redis", port=6379)

@app.post("/search") 
async def search(query: str): 
    cache_key = f"search:{query}" 
    cached = await redis_client.get(cache_key)

    if cached: 
        return {"from_cache": True, "results": json.loads(cached)}

    request_id = str(uuid4()) 
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKERS) 
    await producer.start() 

    try: 
        await producer.send(REQUEST_TOPIC, json.dumps({ "query": query, 
                                                        "request_id": request_id 
                                                        }).encode('utf-8')) 

    finally: 
        await producer.stop() 

    consumer = AIOKafkaConsumer( RESPONSE_TOPIC,
                                bootstrap_servers=KAFKA_BROKERS,
                                group_id="client_group" ) 
    await consumer.start() 

    try: 
        async for msg in consumer: 
            response = json.loads(msg.value.decode('utf-8')) 
            if response.get("request_id") == request_id: 
                return response 

    finally: 
        await consumer.stop()