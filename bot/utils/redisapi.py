import aioredis
import asyncio


async def get_redis_connection():
    redis = await aioredis.from_url(
        'redis://redis-16498.c328.europe-west3-1.gce.redns.redis-cloud.com:16498',
        password='DPa87sxifzxNOhE4sWL7q5PWdKDMCm6S',  # если требуется аутентификация
        encoding='utf-8'
    )
    return redis


async def store_payment_link(link: str, link_id: str, timeout: int = 3600):
    redis = await get_redis_connection()
    await redis.set(link_id, link, ex=timeout)
    redis.close()
    await redis.wait_closed()


async def get_payment_link(link_id: str):
    redis = await get_redis_connection()
    link = await redis.get(link_id, encoding='utf-8')
    redis.close()
    await redis.wait_closed()
    return link


async def main():
    redis = await get_redis_connection()
    await redis.set('key1', 'value1')
    value = await redis.get('key')
    print(value)
    redis.close()
    await redis.wait_closed()

asyncio.run(main())