import asyncio
import os

from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Update

from bot.handlers.user_handlers import command_router
from bot.handlers.callbacks import callback_router


async def on_startup(app: web.Application):
    load_dotenv('.env')

    token = os.getenv("TOKEN_TG")
    bot = Bot(token)
    dp = Dispatcher()
    dp.include_router(command_router)
    dp.include_router(callback_router)

    # Установка вебхука
    webhook_url = os.getenv("WEBHOOK_URL")
    await bot.set_webhook(webhook_url)

    app['bot'] = bot
    app['dp'] = dp


async def on_shutdown(app: web.Application):
    bot = app['bot']
    await bot.delete_webhook()
    await bot.session.close()


async def handle_update(request: web.Request):
    bot = request.app['bot']
    dp = request.app['dp']

    update = Update(**await request.json())
    await dp.process_update(update)
    return web.Response()


app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.router.add_post('/webhook', handle_update)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=int(os.getenv('PORT', 3000)))
