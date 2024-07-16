import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from aiogram import Bot
from dotenv import load_dotenv
import os

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
                    await bot.send_message(user_id, "Поздравляем вы обладатель подписки NockVPN ")
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


async def get_redis_connection():
    redis = await aioredis.from_url(
        'redis://redis-16498.c328.europe-west3-1.gce.redns.redis-cloud.com:16498',
        password='DPa87sxifzxNOhE4sWL7q5PWdKDMCm6S',  # если требуется аутентификация
        encoding='utf-8'
    )
    return redis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
