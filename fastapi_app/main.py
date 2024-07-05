import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from bot.utils.base64coding import decode
from bot.utils.marzhapi import get_user_sub

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = FastAPI()


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
