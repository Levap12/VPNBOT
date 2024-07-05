import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import logging

from bot.utils.base64coding import decode
from dotenv import load_dotenv

from bot.utils.marzhapi import get_panel_and_token

load_dotenv('../.env')
SUB_URL = os.getenv("SUB_URL")
PANEL_URL= os.getenv("PANEL_URL")

app = FastAPI()
logging.basicConfig(level=logging.INFO)


async def get_user_sub(user_id: int):
    logging.info(f"Getting panel and token for user_id: {user_id}")
    panel, token = await get_panel_and_token()
    result = await panel.get_user(str(user_id), token=token)
    logging.info(f"User subscription URL: {result.subscription_url}")
    return f"{PANEL_URL}{result.subscription_url}"


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
