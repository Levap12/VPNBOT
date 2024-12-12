import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from aiogram import Bot
from dotenv import load_dotenv
import os
from ipaddress import ip_network, ip_address
from bot.utils.base64coding import decode
from bot.utils.marzhapi import get_user_sub
from bot.utils.payment import verify_sign
from bot.utils.marzhapi import extend_expire
import aioredis

import json
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
load_dotenv('../.env')
TOKEN_TG = os.getenv("TOKEN_TG")
bot = Bot(token=TOKEN_TG)
processed_payments = set()

ALLOWED_IPS = [
    ip_network("185.71.76.0/27"),
    ip_network("185.71.77.0/27"),
    ip_network("77.75.153.0/25"),
    ip_network("77.75.156.11/32"),
    ip_network("77.75.156.35/32"),
    ip_network("77.75.154.128/25"),
    ip_network("2a02:5180::/32")
]

@app.get("/sub/{user_id}")
async def redirect_user(user_id):
    try:
        logging.info(f"Received user_id: {user_id}")
        decoded_user_id = decode(user_id)
        logging.info(f"Decoded user_id: {decoded_user_id}")

        # Сделать запрос к сервису для получения конечного URL
        redirect_url = await get_user_sub(decoded_user_id)
        logging.info(f"Redirect URL: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payment")
async def payment(request: Request):
    params = request.query_params
    mounts = int(params.get('mounts'))
    user_id = params.get('user_id')
    user_ip = request.client.host
    logging.info(f"Received mounts: {mounts}, user_id: {user_id}, user_ip: {user_ip}")
    if mounts not in [1, 3, 6]:
        raise HTTPException(status_code=400, detail="Invalid mounts value")

    link, error = await payment.create_payment(user_id, mounts, user_ip)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"link": link}
# ae00-178-90-225-38.ngrok-free.app/payment?user_id=1546789&mounts=1


@app.get("/payment/callback")
async def payment_notify(request: Request):
    params = request.query_params
    unique_id = params.get('unique_id')
    sign = params.get('sign')
    amount = params.get('amount')
    status = params.get('status')
    additional = params.get('additional')

    logging.info(f"== unique_id: {unique_id}, sign: {sign}, amount: {amount}, status: {status}, additional: {additional}")

    # Проверка корректности подписи
    if not await verify_sign(unique_id, amount, sign):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Обработка дополнительной информации
    if additional:
        try:
            additional_data = json.loads(additional)
            user_id = additional_data.get('user_id')
            months = additional_data.get('months')
            if user_id and months:
                await extend_expire(user_id, months)
                try:
                    await bot.send_message(user_id, f"Подписка обновлена на {months} мес.")
                    logger.info(f"Message sent to chat_id={user_id}")
                except Exception as e:
                    logger.error(f"Failed to send message: {e}", exc_info=True)
            else:
                logging.error(f"Invalid additional data: {additional}")
                raise HTTPException(status_code=400, detail="Invalid additional data")
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format for additional: {additional}")
            raise HTTPException(status_code=400, detail="Invalid JSON format for additional")

    return {"message": "Payment processed successfully"}


def check_ip(request: Request) -> bool:
    """Проверка IP-адреса запроса"""
    ip = request.client.host
    logger.debug(f"Request IP: {ip}")
    return any(ip_address(ip) in network for network in ALLOWED_IPS)

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        # Получаем тело запроса и подпись
        body = await request.body()
        signature = request.headers.get('x-signature', '')

        # Проверка IP-адреса
        if not check_ip(request):
            logger.error(f"Invalid IP address: {request.client.host}")
            raise HTTPException(status_code=403, detail="Forbidden: Invalid IP address")

        # Логируем полученные данные для отладки
        logger.debug(f"Received body: {body.decode('utf-8')}")
        logger.debug(f"Received signature: {signature}")


        # Обрабатываем событие
        data = json.loads(body.decode('utf-8'))
        event = data.get('event')
        object_data = data.get('object')

        # Проверка, что платеж не был обработан ранее
        payment_id = object_data.get('id')
        if payment_id in processed_payments:
            logger.info(f"Payment {payment_id} already processed.")
            return {"status": "ok"}  # Возвращаем успешный ответ без обработки

        # Добавляем платеж в список обработанных
        processed_payments.add(payment_id)

        logger.debug(f"Event: {event}, Object: {object_data}")

        # Проверка, что статус платежа успешен
        if event == 'payment.succeeded' and object_data.get('status') == 'succeeded':
            user_id = int(object_data.get('metadata', {}).get('user_id'))
            months = int(object_data.get('metadata', {}).get('months'))
            # Обрабатываем успешный платеж
            logger.info(f"Payment succeeded: {object_data}")
            logger.info(f"User id: {user_id}")

            await extend_expire(user_id, months)

            try:
                await bot.send_message(user_id, f"Подписка обновлена на {months} мес.")
                logger.info(f"Message sent to chat_id={user_id}")
            except Exception as e:
                logger.error(f"Failed to send message: {e}", exc_info=True)

            # Здесь добавьте логику обработки успешного платежа
        else:
            logger.warning(f"Received event with invalid status: {object_data.get('status')}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_redis_connection():
    redis = await aioredis.from_url(
        'redis://redis-16498.c328.europe-west3-1.gce.redns.redis-cloud.com:16498',
        password='DPa87sxifzxNOhE4sWL7q5PWdKDMCm6S',  # если требуется аутентификация
        encoding='utf-8'
    )
    return redis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3055)
