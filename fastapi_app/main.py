import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx

from bot.utils.base64coding import decode
from dotenv import load_dotenv

from bot.utils.marzhapi import get_user_sub

load_dotenv('../.env')
SUB_URL = os.getenv("SUB_URL")
app = FastAPI()

@app.get("/sub/{user_id}")
async def redirect_user(user_id):
    try:
        # Сделать запрос к сервису для получения конечного URL
        redirect_url = await get_user_sub(decode(user_id))
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
