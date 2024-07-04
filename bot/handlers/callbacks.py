from aiogram import F, Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards import user_keyboards
from bot.handlers.user_handlers import cmd_start
import os
from datetime import datetime, timedelta
from bot.utils import marzhapi

callback_router = Router()

# @callback_router.callback_query(F.data == 'first_connect')
# async def first_connect(callback: CallbackQuery):
#     link = await marzhapi.crate_trial(callback.from_user.id)
#     text = '🪐 Подключение к Vless:' \
#            '\n' \
#            f'\n<code>{link}</code>' \
#            '\n👆 Нажмите чтобы скопировать!'
#
#     await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_firstmsg_kb(), parse_mode='HTML')


@callback_router.callback_query(F.data == 'profile')
async def profile_cb(callback: CallbackQuery):
    user_info = await marzhapi.get_user_info(callback.from_user.id)

    if user_info["subscription_status"] == 'active':
        sub_status = "✅ Активна"
    elif user_info["subscription_status"] == 'disabled':
        sub_status = "❌ Не активна"

    else:
        sub_status = "❓ Неизветсна ошибка"

    text = f'<b>Подписка: {sub_status}</b>\n' \
           f'├ ID: {callback.from_user.id}\n' \
           f'├ Осталось дней: {user_info["remaining_days"]}\n' \
           f'└ Активна до: {user_info["expire_date"]}'#├└

    await callback.message.edit_text(text=text,reply_markup=user_keyboards.get_profile_kb(),parse_mode='HTML')


@callback_router.callback_query(F.data == 'back_to_menu')
async def back_to_main_cb(callback: CallbackQuery):
    main_menu = 'Nock VPN — безопасная защита для вашей онлайн-жизни.\n' \
                '\n' \
                '🔥 Приобретайте подписку Nock VPN от 200₽\n' \
                '\n' \
                '⚡️ Подключайтесь к VPN, жмите на кнопку «Подключится»\n' \
                '\n' \
                'Вы можете управлять ботом следующими командами:'

    await callback.message.edit_text(text=main_menu,reply_markup=user_keyboards.get_main_kb())


@callback_router.callback_query(F.data == 'buyvpn')
async def buyvpn_cb(callback: CallbackQuery):
    text = 'Для полного доступа выберите удобный для вас тариф:' \
           '\n\n190₽ / 1 мес' \
           '\n500₽ / 3 мес' \
           '\n900₽ / 6 мес' \
           '\n\n💳 К оплате принимаются карты РФ:' \
           '\nVisa, MasterCard, МИР и криптовалюты.'


    await callback.message.edit_text(text=text,reply_markup=user_keyboards.get_buyvpn_kb())


async def handle_subscription(callback: CallbackQuery, months: int):
    if months == 1:
        month_text = "месяц"
    elif 2 <= months <= 4:
        month_text = "месяца"
    else:
        month_text = "месяцев"

    payment_url = f'https://payment.example.com/{months}_months'  # Замените на реальную ссылку
    crypto_payment_url = f'https://crypto-payment.example.com/{months}_months'  # Замените на реальную ссылку

    text = f'Доступ на {months} {month_text}'
    await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_payment_kb(months, payment_url, crypto_payment_url))


@callback_router.callback_query(F.data.startswith('test_payment_'))
async def test_payment_cb(callback: CallbackQuery):
    months = int(callback.data.split('_')[-1])
    if months == 1:
        month_text = "месяц"
    elif months == 3:
        month_text = "месяца"
    elif months == 6:
        month_text = "месяцев"
    else:
        month_text = "месяцев"

    await marzhapi.extend_expire(callback.from_user.id,months)

    text = f'Оплата за {months} {month_text} успешно выполнена! Спасибо за покупку.'
    await callback.message.edit_text(text=text,reply_markup=user_keyboards.get_mainmenu_kb())


# Обработчики для каждого периода подписки
@callback_router.callback_query(F.data == 'buyvpn_1')
async def buyvpn_1_cb(callback: CallbackQuery):
    await handle_subscription(callback, 1)

@callback_router.callback_query(F.data == 'buyvpn_3')
async def buyvpn_3_cb(callback: CallbackQuery):
    await handle_subscription(callback, 3)

@callback_router.callback_query(F.data == 'buyvpn_6')
async def buyvpn_6_cb(callback: CallbackQuery):
    await handle_subscription(callback, 6)


@callback_router.callback_query(F.data == 'connect')
async def trial_shadowsocks_cb(callback: CallbackQuery):
    text = 'Выберите тип подключения 👇\n' \
           'Рекомендуем Vless'
    await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_connect_kb())


@callback_router.callback_query(F.data == 'vless')
async def trial_vless_cb(callback: CallbackQuery):
    link = await marzhapi.crate_user(callback.from_user.id)
    text = '🪐 Подключение к VPN:' \
           '\n' \
           f'\n<code>{link}</code>' \
           '\n👆 Нажмите (тапните) чтобы скопировать и добавьте в приложение' \
           '\n' \
           '\nЕсли приложение уже установлено - воспользуйтесь <b>быстрым подключением</b>' \
           '\n- <a href="https://apps.apple.com/us/app/streisand/id6450534064">Streisand</a> - для iOS 🍏' \
           '\n- <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">v2rayNG</a> - для Android 🤖' \
           '\n' \
           '\n<a href="">iOS</a>' \
           '\n<a href="">Android</a>' \
           '\n' \
           '\n⭐️ Если у вас Android(v2rayNG) - нажмите в приложении "..." - Обновить подписку' \
           '\n' \
           '\nПосмотреть подробную инструкцию 👇'
    await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_vless_con_kb(), parse_mode='HTML',disable_web_page_preview=True)



# /sub/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTExMSIsImFjY2VzcyI6InN1YnNjcmlwdGlvbiIsImlhdCI6MTcxNjQwOTE0Nn0.0JnskQ2WHt_JEj6v5xUzD85-vjcHzi1eF92IyS4URug
# /sub/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTExMSIsImFjY2VzcyI6InN1YnNjcmlwdGlvbiIsImlhdCI6MTcxNjQxMDA5OX0.7MjY1IDfK1T97zSUrWH-e42ySV3mreD_lSL4qYnkJNc


# @callback_router.callback_query(F.data.startswith('outline'))
# async def trial_shadowsocks_cb(callback: CallbackQuery):
#     text = '🪐 Подключение к Outline VPN:' \
#            '\n\n<code>ssconf://users.outline.artydev.ru/conf/959fc2d1ec5e0x1af70d27#nRomania</code>' \
#             '\n👆 Нажмите чтобы скопировать!' \
#            '\n\nПосмотреть 👉 инструкцию (https://telegra.ph/Podklyuchenie-k-Outline-VPN-08-11)'
#
#     await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_connected_kb(), parse_mode='HTML',disable_web_page_preview=True)




# @callback_router.callback_query(F.data.startswith('trial_shadowsocks_'))
# async def trial_shadowsocks_cb(callback: CallbackQuery):
#     country_id = callback.data.split('_')[-1]
#     print(f'{country_id}')
#     if country_id == "nl":
#         panel = Marzban(os.getenv("MARZH_LOGIN"), os.getenv("MARZH_PWD"), "https://vm13139.vpsone.xyz")
#         token = await panel.get_token()
#         expire_time = datetime.utcnow() + timedelta(days=1)  # Установка времени истечения срока действия на 1 день
#         expire_timestamp = int(expire_time.timestamp())
#         user = User(
#             username="new_user",  # Задайте уникальное имя пользователя
#             proxies={
#                 "shadowsocks": {}
#             },
#             inbounds={"shadowsocks": ["Shadowsocks TCP"]},  # Установка входящих соединений для Shadowsocks
#             expire=expire_timestamp,  # Установка времени истечения срока действия
#             data_limit=1024 * 1024 * 1024 * 15,  # Установка лимита данных, если необходимо
#             data_limit_reset_strategy="no_reset",  # Стратегия сброса лимита данных
#             status="active"  # Статус пользователя
#         )
#
#         result = await panel.add_user(user=user, token=token)
#
#         await callback.message.edit_text(text=result.links[0], reply_markup=await user_keyboards.get_trial_shadowsocks_countries_kb())

