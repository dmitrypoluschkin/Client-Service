from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from app.kafka_producer import send_to_kafka
from app.kafka_consumer import consume_response
from app.redis_client import get_redis, set_redis
import json
import asyncio
import uuid

app = FastAPI()

class SearchQuery(BaseModel):
    query: str

@app.post("/search", status_code=200)
async def search(search_query: SearchQuery, redis=Depends(get_redis)):
    query = search_query.query
    cache_key = f"search_query_{query}"

    # Проверка кэша
    cached_result = await redis.get(cache_key)
    if cached_result:
        return {"message": "Results from cache", "data": json.loads(cached_result)}

    # Генерация уникального ID запроса
    request_id = str(uuid.uuid4())

    # Отправка запроса в Kafka
    await send_to_kafka({"query": query, "request_id": request_id})

    # Ожидание ответа из Kafka
    response = await consume_response(request_id)
    if not response:
        raise HTTPException(status_code=504, detail="No response from search service")

    # Сохранение результата в Redis
    await set_redis(cache_key, json.dumps(response), ex=3600)

    return {"message": "Search processed successfully", "data": response}