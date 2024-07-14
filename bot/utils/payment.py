import os
import aiohttp
import hashlib
from dotenv import load_dotenv
import datetime
import aioredis
load_dotenv('../.env')

TOKEN_TWP = os.getenv("TOKEN_TWP")
SHOP_ID_TWP = os.getenv("SHOP_ID_TWP")

API_URL = 'https://techwhizpay.ru/api/createOrder'


async def create_payment(user_id, months):
    redis = await get_redis_connection()
    link_id = f"{user_id}_{months}"
    payment_link = await redis.get(link_id)

    if payment_link:
        return payment_link, None

    unique_id = generate_unique_id()
    amount, description = get_amount_and_description(months)

    if amount is None:
        return None, "Invalid months value"

    params = {
        'token': TOKEN_TWP,
        'unique_id': unique_id,
        'amount': amount,
        'shop_id': SHOP_ID_TWP,
        'description': description,
        'user_ip': "0.0.0.0",
        'additional': {"user_id":user_id,"months":months}
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, data=params) as response:
            result = await response.json()

    if result['data']['error'] == 0:
        link = result['data']['link']
        await redis.set(link_id, link, ex=3600)
        return link, None
    else:
        return None, result['data']['message']


def generate_unique_id():
    now = datetime.datetime.now()
    unique_id = now.strftime("%d%m%y%H%M")
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