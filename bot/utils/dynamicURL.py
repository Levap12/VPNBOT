from fastapi import FastAPI, HTTPException
from typing import Union
from pydantic import BaseModel
from database import database, keys
from datetime import datetime, timedelta
from database import database, keys
from marzpy import Marzban
from marzpy.api.user import User
import base64
import json

app = FastAPI()


class KeyCreate(BaseModel):
    user_id: str
    server: str
    port: int


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def create_marzban_user(user_id: str):
    panel = Marzban("username", "password", "https://example.com")
    token = await panel.get_token()

    user = User(
        username=user_id,
        proxies={"shadowsocks": {}},
        inbounds={"shadowsocks": ["shadowsocks"]},
        expire=(datetime.now() + timedelta(days=3)).timestamp(),
        data_limit=0,
        status="active",
        data_limit_reset_strategy="no_reset"
    )
    result = await panel.add_user(user=user, token=token)
    return result


@app.get("/outline/getconfig/{user_id}")
async def get_config(user_id: Union[str, int]):
    # Здесь должен быть код для получения данных из базы данных
    # Например, получаем данные сервера, порт, пароль и метод шифрования
    if user_id == "levap12":
        config_data = {
            "server": "vm13139.vpsone.xyz",
            "port": "1080",
            "password": "Ksi2f26M9MO3OXULIe_95A",
            "method": "chacha20-ietf-poly1305"
        }
    
    # Генерация Shadowsocks URI из полученных данных
    # ss_uri = f"ss://{config_data['method']}:{config_data['password']}@{config_data['server']}:{config_data['port']}"
    return config_data


@app.get("/get_config/{user_id}")
async def get_config(user_id: str):
    query = keys.select().where(keys.c.user_id == user_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    config = {
        "server": result["server"],
        "server_port": result["port"],
        "password": result["password"],
        "method": result["method"]
    }
    config_str = json.dumps(config)
    config_encoded = base64.urlsafe_b64encode(config_str.encode()).decode()
    return {"config": config_encoded}


@app.get("/get_link/{key_id}")
async def get_link(key_id: int):
    query = keys.select().where(keys.c.id == key_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Key not found")

    return {"outline_link": result["config_url"]}