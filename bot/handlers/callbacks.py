from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from bot.keyboards import user_keyboards
import os
from bot.utils import marzhapi
import asyncio
callback_router = Router()
from bot.utils.base64coding import encode
from dotenv import load_dotenv
from bot.utils.payment import create_payment

load_dotenv('../.env')
SUB_URL = os.getenv("SUB_URL")

# @callback_router.callback_query(F.data == 'first_connect')
# async def first_connect(callback: CallbackQuery):
#     link = await marzhapi.crate_trial(callback.from_user.id)
#     text = '🪐 Подключение к Vless:' \
#            '\n' \
#            f'\n<code>{link}</code>' \
#            '\n👆 Нажмите чтобы скопировать!'
#
#     await callback.message.edit_text(text=text, reply_markup=user_keyboards.get_firstmsg_kb(), parse_mode='HTML')

user_last_interaction = {}
async def handle_message_edit(callback: CallbackQuery, new_text: str, new_reply_markup):
    user_id = callback.from_user.id
    current_time = asyncio.get_event_loop().time()

    # Проверка, что прошло достаточно времени с последнего взаимодействия
    if user_id in user_last_interaction:
        last_time = user_last_interaction[user_id]
        if current_time - last_time < .5:  # Например, 1 секунда
            await callback.answer("Подождите немного перед следующим нажатием.")
            return

    user_last_interaction[user_id] = current_time

    # Проверка, изменился ли текст сообщения или его разметка
    if callback.message.text != new_text or callback.message.reply_markup != new_reply_markup:
        await callback.message.edit_text(text=new_text, reply_markup=new_reply_markup, parse_mode='HTML', disable_web_page_preview=True)
    else:
        await callback.answer("Сообщение не изменено.")


@callback_router.callback_query(F.data == 'profile')
async def profile_cb(callback: CallbackQuery):
    user_info = await marzhapi.get_user_info(callback.from_user.id)

    if user_info["subscription_status"] == 'active':
        sub_status = "✅ Активна"
    elif user_info["subscription_status"] == 'disabled' or 'expired':
        sub_status = "❌ Не активна"

    else:
        sub_status = "❓ Неизветсна ошибка"

    text = f'<b>Подписка: {sub_status}</b>\n' \
           f'├ ID: {callback.from_user.id}\n' \
           f'├ Осталось дней: {user_info["remaining_days"]}\n' \
           f'└ Активна до: {user_info["expire_date"]}'#├└

    await handle_message_edit(callback, text, user_keyboards.get_profile_kb())


@callback_router.callback_query(F.data == 'back_to_menu')
async def back_to_main_cb(callback: CallbackQuery):
    main_menu = 'Nock VPN — безопасная защита для вашей онлайн-жизни.\n' \
                '\n' \
                '🔥 Приобретайте подписку Nock VPN от 190₽\n' \
                '\n' \
                '⚡️ Подключайтесь к VPN, жмите на кнопку «Подключится»\n' \
                '\n' \
                'Вы можете управлять ботом следующими командами:'

    await handle_message_edit(callback, main_menu, user_keyboards.get_main_kb())


@callback_router.callback_query(F.data == 'buyvpn')
async def buyvpn_cb(callback: CallbackQuery):
    text = 'Для полного доступа выберите удобный для вас тариф:' \
           '\n\n190₽ / 1 мес' \
           '\n500₽ / 3 мес' \
           '\n900₽ / 6 мес' \
           '\n\n💳 К оплате принимаются карты РФ:' \
           '\nVisa, MasterCard, МИР и криптовалюты.'


    await handle_message_edit(callback, text, user_keyboards.get_buyvpn_kb())


async def handle_subscription(callback: CallbackQuery, months: int):
    user_id = callback.from_user.id

    if months == 1:
        month_text = "месяц"
    elif 2 <= months <= 4:
        month_text = "месяца"
    else:
        month_text = "месяцев"

    text = f'ℹ️ Доступ на {months} {month_text}. ' \
           f'Оплата переводом на Т-Банк' \
           f'\n\n❗️Для оплаты напишите оператору 👇'
    payment_link = "https://t.me/NockVPN_support"
    await handle_message_edit(callback, text, user_keyboards.get_payment_kb(months, payment_link, None))
    # payment_link, error = await create_payment(user_id, months)
    # if payment_link:
    #     text = f'Доступ на {months} {month_text}'
    #     crypto_payment_url = f'https://crypto-payment.example.com/{months}_months'  # Замените на реальную ссылку
    #     await handle_message_edit(callback, text, user_keyboards.get_payment_kb(months, payment_link, crypto_payment_url))
    # else:
    #     await callback.message.answer(f"Ошибка создания ссылки: {error}")
    # await callback.message.answer(f'Для оплаты обратитесь в <a href="https://t.me/NockVPN_support">поддержку</a>', parse_mode='HTML')

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
    await handle_message_edit(callback, text, user_keyboards.get_mainmenu_kb())


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
    await handle_message_edit(callback, text, user_keyboards.get_connect_kb())


@callback_router.callback_query(F.data == 'vless')
async def trial_vless_cb(callback: CallbackQuery):
    text = '🪐 Подключение к VPN:' \
           '\n' \
           '\nВаша ссылка:' \
           f'\n└<code>{SUB_URL}/{encode(callback.from_user.id)}</code>' \
           '\nНажмите (тапните) чтобы скопировать и добавьте в приложение' \
           '\n' \
           '\nЕсли приложение уже установлено - воспользуйтесь <b>быстрым подключением</b>' \
           '\n- <a href="https://apps.apple.com/us/app/streisand/id6450534064">Streisand</a> - для iOS 🍏' \
           '\n- <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">v2rayNG</a> - для Android 🤖' \
           '\n' \
           '\nПодключить в <b>1 клик!</b>' \
           f'\n<a href="https://apps.artydev.ru/?url=streisand://import/{SUB_URL}/{encode(callback.from_user.id)}#Nock%20VPN">iOS</a>' \
           f'\n<a href="https://apps.artydev.ru/?url=v2rayng://install-config?url={SUB_URL}/{encode(callback.from_user.id)}">Android</a>' \
           '\n' \
           '\n⭐️ Если у вас Android(v2rayNG) - нажмите в приложении "..." - Обновить подписку' \
           '\n' \
           '\nПосмотреть подробную инструкцию 👇'
    await handle_message_edit(callback, text, user_keyboards.get_vless_con_kb())


@callback_router.message(F.content_type == 'video')
async def get_file_id(message: types.Message):
    # Получаем file_id отправленного видео
    file_id = message.video.file_id
    await message.reply(f"Ваш file_id: {file_id}")


# Обработчик callback-запросов для отправки видео
@callback_router.callback_query(lambda callback: callback.data in ['video_ios', 'video_mac', 'video_win', 'video_android'])
async def send_video(callback: types.CallbackQuery):
    try:
        # Словарь с параметрами для разных платформ
        video_data = {
            'video_ios': {
                'file_id': 'BAACAgQAAxkBAAIBOmcaHKmob-v6srPRPIM16-Il2YYmAAIkGAACmHxpUHQBCLbNDQn9NgQ',
                'caption': "Видео инструкция для IOS 🍏"
            },
            'video_mac': {
                'file_id': 'BAACAgQAAxkBAAIBPWcaHRElJOlM15LVME9Sa2w5X1MyAALbFQACmr6wUHidqln6cqO-NgQ',
                'caption': "Видео инструкция для mac OS"
            },
            'video_win': {
                'file_id': 'BAACAgIAAxkBAAMiZxj65u4ZxQldw3Sxg3H7KxL2-v0AAvJVAAJcmMlIyZHuytJiyn82BA',
                'caption': "Видео инструкция для Windows"
            },
            'video_android': {
                'file_id': 'BAACAgIAAxkBAAMiZxj65u4ZxQldw3Sxg3H7KxL2-v0AAvJVAAJcmMlIyZHuytJiyn82BA',
                'caption': "Видео инструкция для Android"
            }
        }

        # Получаем параметры в зависимости от платформы
        video_info = video_data.get(callback.data, {})
        file_id = video_info.get('file_id')
        caption = video_info.get('caption', "Видео инструкция")

        # Клавиатура для всех платформ одинакова
        keyboard = user_keyboards.get_support_kb()

        # Отправляем видео
        if file_id:
            await callback.message.answer_video(
                video=file_id,
                caption=caption
            )

            # Отправляем текст с клавиатурой после видео
            await callback.message.answer(
                text='🌐 Проблемы с подключением ???\n\n❗️Напишите оператору, мы работаем 24/7 👇',
                reply_markup=keyboard
            )
        else:
            await callback.message.answer("Не удалось найти видео для выбранной платформы.")

    except Exception as e:
        await callback.message.answer(f"Ошибка при отправке: {str(e)}")



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

