import asyncio

from aiocache import cached
from marzpy import Marzban
from marzpy.api.user import User
from datetime import datetime, timedelta
from aiohttp.client_exceptions import ClientResponseError,ClientError, InvalidURL
from dotenv import load_dotenv
import os
from dateutil.relativedelta import relativedelta
import logging


load_dotenv('../.env')
LOGIN = os.getenv("MARZH_LOGIN")
PASS = os.getenv("MARZH_PWD")
PANEL_URL = os.getenv("PANEL_URL")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@cached(ttl=600)
async def get_panel_and_token():
    panel = Marzban(LOGIN, PASS, PANEL_URL)
    try:
        token = await panel.get_token()
        logging.debug(f"Token received: {token}")
        return panel, token
    except (ClientError, InvalidURL) as ex:
        logging.error(f"Failed to get token: {ex}")
        raise Exception(f"Failed to get token: {ex}")


async def get_user_sub(user_id: int):
    logging.debug(f"Getting panel and token for user_id: {user_id}")
    panel, token = await get_panel_and_token()
    result = await panel.get_user(str(user_id), token=token)
    logging.debug(f"User subscription URL: {result.subscription_url}")
    return f"{PANEL_URL}{result.subscription_url}"


async def extend_expire(user_id: int, months: int):
    logger.debug(f"extend_expire called with user_id={user_id}, months={months}")

    try:
        panel, token = await get_panel_and_token()
        logger.debug(f"Got panel and token: panel={panel}, token={token}")

        # Получить текущие данные пользователя
        user_data = await panel.get_user(str(user_id), token=token)
        logger.debug(f"Got user data: {user_data}")

        # Проверить текущий срок действия подписки
        current_expire_timestamp = user_data.expire
        if current_expire_timestamp is None:
            current_expire_time = datetime.utcnow()
        else:
            current_expire_time = datetime.utcfromtimestamp(current_expire_timestamp)
        now = datetime.utcnow()

        logger.debug(f"Current expire time: {current_expire_time}, now: {now}")

        # Определить новую дату истечения срока действия
        if current_expire_time < now:
            # Если срок действия истек, прибавить месяцы от сегодняшнего дня
            new_expire_time = now + relativedelta(months=months)
            user_data.status = 'active'
            user_data.data_limit = 0
        else:
            # Если срок действия еще активен, прибавить месяцы от текущего срока действия
            new_expire_time = current_expire_time + relativedelta(months=months)

        new_expire_timestamp = int(new_expire_time.timestamp())
        logger.debug(f"New expire time: {new_expire_time} (timestamp: {new_expire_timestamp})")

        user = User(
            username=user_data.username,  # Используйте текущее имя пользователя
            proxies=user_data.proxies,  # Используйте текущие прокси данные
            inbounds=user_data.inbounds,  # Используйте текущие входящие соединения
            expire=new_expire_timestamp,  # Установить новую дату истечения срока действия
            data_limit=user_data.data_limit,  # Используйте текущий лимит данных
            status=user_data.status  # Используйте текущий статус пользователя
        )

        result = await panel.modify_user(str(user_id), token=token, user=user)
        logger.debug(f"User modified successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in extend_expire: {e}", exc_info=True)
        raise


async def crate_user(user_id: int):
    panel, token = await get_panel_and_token()
    expire_time = datetime.utcnow() + timedelta(days=3)  # Установка времени истечения срока действия на 1 день
    expire_timestamp = int(expire_time.timestamp())
    user = User(
        username=str(user_id),  # Задайте уникальное имя пользователя
        proxies={
            "vless": {}
        },
        inbounds={"vless": ["VLESS TCP REALITY"]},  # Установка входящих соединений для Shadowsocks
        expire=expire_timestamp,  # Установка времени истечения срока действия
        data_limit=1024*1024*1024*25,  # Установка лимита данных, если необходимо
        data_limit_reset_strategy="no_reset",  # Стратегия сброса лимита данных
        status="active"  # Статус пользователя
    )
    try:
        result = await panel.add_user(user=user, token=token)
        print(result.links[0])
        return result.links[0]
    except ClientResponseError as e:
        if e.status == 409:
            result = await panel.get_user(str(user_id), token=token)
            print(result.subscription_url)
            return f"{PANEL_URL}{result.subscription_url}"
        else:
            raise e


async def get_user_info(user_id):
    panel, token = await get_panel_and_token()
    user_data = await panel.get_user(str(user_id), token=token)

    # Статус подписки
    subscription_status = user_data.status

    # Дата окончания подписки
    expire_timestamp = user_data.expire

    if expire_timestamp is None:
        # Если подписка бесконечна
        expire_formatted = "∞"
        remaining_days = "∞"  # или другое значение, чтобы обозначить бесконечность
    else:
        # Если подписка имеет срок окончания
        expire_date = datetime.utcfromtimestamp(expire_timestamp)
        expire_formatted = expire_date.strftime('%d.%m.%Y')

        # Осталось дней
        now = datetime.utcnow()
        remaining_days = (expire_date - now).days if expire_date > now else 0

    return {
        "subscription_status": subscription_status,
        "remaining_days": remaining_days,
        "expire_date": expire_formatted
    }


# async def main():
#     result = await extend_expire("452398375",1)
#     print(result.expire)
#     # result = await crate_shadow_trial("1231231")
#     # print(result)


    # username = 'levap12'
    # password = 'M@ve1207'
    # panel = Marzban(username, password, "https://vm13139.vpsone.xyz")
    # token = await panel.get_token()
    # # Дальнейшие операции с использованием токена, например:
    # # expire_time = datetime.utcnow() + timedelta(days=1)  # Установка времени истечения срока действия на 1 день
    # # expire_timestamp = int(expire_time.timestamp())
    # expire_time = datetime.utcnow() + relativedelta(minutes=61)
    # expire_timestamp = int(expire_time.timestamp())
    # print(expire_timestamp)
    # user = User(
    #     username="452398375",  # Задайте уникальное имя пользователя
    #     proxies={
    #         "vless": {}
    #     },
    #     inbounds={"vless": ["VLESS TCP REALITY"]},  # Установка входящих соединений для Shadowsocks
    #     expire=expire_timestamp, # Установка времени истечения срока действия
    #     data_limit=0,  # Установка лимита данных, если необходимо,  # Стратегия сброса лимита данных
    #     status="active"  # Статус пользователя
    # )
    # result = await panel.modify_user('452398375',user=user, token=token)
    #
    # user_info = await panel.get_user('asdd', token=token)
    # print(result.inbounds)

    # Вывод ключа подключения
    # print(f"Shadowsocks connection key: {user_info['ss_connect_key']}")


# asyncio.run(main())