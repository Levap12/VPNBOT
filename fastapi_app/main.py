from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import bot.utils.marzhapi

app = FastAPI()

SERVICE_URL = "https://example.com/get_redirect_url"  # URL вашего сервиса для получения конечного URL


@app.get("/sub/{user_id}")
async def redirect_user(user_id: int):
    # Сделать запрос к сервису для получения конечного URL
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URL}?user_id={user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch redirect URL")

        redirect_url = response.json().get("redirect_url")
        if not redirect_url:
            raise HTTPException(status_code=400, detail="No redirect URL found")

    # Вернуть редирект на полученный URL
    return RedirectResponse(url=redirect_url)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
