import json
import os
import aiohttp
import hashlib
from dotenv import load_dotenv
import datetime
import aioredis
import logging
load_dotenv('../.env')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOKEN_TWP = os.getenv("TOKEN_TWP")
SHOP_ID_TWP = os.getenv("SHOP_ID_TWP")

API_URL = 'https://techwhizpay.ru/api/createOrder'


async def create_payment(user_id, months):
    logger.debug(f"create_payment called with user_id={user_id}, months={months}")

    try:
        redis = await get_redis_connection()
        logger.debug("Connected to Redis")

        link_id = f"{user_id}_{months}"
        payment_link = await redis.get(link_id)

        if payment_link:
            logger.debug(f"Found existing payment link: {payment_link}")
            return payment_link, None

        unique_id = generate_unique_id()
        logger.debug(f"Generated unique_id: {unique_id}")

        amount, description = get_amount_and_description(months)
        logger.debug(f"Got amount and description: amount={amount}, description={description}")

        if amount is None:
            logger.error("Invalid months value")
            return None, "Invalid months value"

        params = {
            'token': TOKEN_TWP,
            'unique_id': unique_id,
            'amount': amount,
            'shop_id': SHOP_ID_TWP,
            'description': description,
            'user_ip': "0.0.0.0",
            'additional': json.dumps({"user_id": user_id, "months": months})
        }
        logger.debug(f"Payment parameters: {params}")

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data=params) as response:
                result = await response.json()
                logger.debug(f"Received response: {result}")

        if result['data']['error'] == 0:
            link = result['data']['link']
            await redis.set(link_id, link, ex=3600)
            logger.debug(f"Payment link created and saved in Redis: {link}")
            return link, None
        else:
            logger.error(f"Error in payment creation: {result['data']['message']}")
            return None, result['data']['message']
    except Exception as e:
        logger.error(f"Error in create_payment: {e}", exc_info=True)
        raise


def generate_unique_id():
    now = datetime.datetime.now()
    unique_id = now.strftime("%d%m%y%H%M%S")
    return unique_id


def get_amount_and_description(mounts):
    if mounts == 1:
        return 190, "NockVPN 1 месяц"
    elif mounts == 3:
        return 500, "NockVPN 3 месяца"
    elif mounts == 6:
        return 900, "NockVPN 6 месяцев"
    else:
        return None, None


async def verify_sign(unique_id, amount, sign):
    # Реализуйте проверку подписи
    calculated_sign = hashlib.sha256(f"{unique_id}:{amount}:{TOKEN_TWP}:{SHOP_ID_TWP}".encode()).hexdigest()
    return calculated_sign == sign

# calculated_sign = hashlib.sha256(f"{807241025}:{190}:OWIU9PI9DIAZGRKK8KPFEJNUQEUDR8FK:{100}".encode()).hexdigest()

#=======================REDIS============================================================

async def get_redis_connection():
    redis = await aioredis.from_url(
        'redis://redis-16498.c328.europe-west3-1.gce.redns.redis-cloud.com:16498',
        password='DPa87sxifzxNOhE4sWL7q5PWdKDMCm6S',  # если требуется аутентификация
        encoding='utf-8'
    )
    return redis