from aiogram import Router,Dispatcher,F,Bot, types
from bot.keyboards.user_keyboards import get_first_start_kb
from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from bot.utils import marzhapi
from dotenv import load_dotenv
import os
command_router = Router()
load_dotenv('../.env')

token = os.getenv("TOKEN_TG")
bot = Bot(token=token)

from bot.utils.logsdb import LogsDB
logs_db = LogsDB()

@command_router.message(CommandStart())
async def cmd_start(message: Message):
    main_menu = f'🖖 Привет {message.from_user.first_name}!' \
                '\nЯ — Nock VPN бот.' \
                '\nЯ подключу вас к VPN за пару простых шагов.' \
                '\nПопробуй бесплатно 72 часа самый быстрый VPN в Европе.' \
                '\nЖми 🔌Подключиться ниже в меню и я помогу настроить VPN на любом устройстве за 2 минуты.\n'
    await message.answer(
        text=main_menu,
        reply_markup=get_first_start_kb(), parse_mode='HTML'
    )
    create_user_result = await marzhapi.crate_user(message.from_user.id) #создание пользователя в панеле VPN
    if create_user_result['status'] == 'ok':
        # Если пользователь успешно создан, отправляем уведомление в группу
        group_message = (
            f'🆕 Новый пользователь подключился!\n'
            f'Имя: {message.from_user.first_name}\n'
            f'ID пользователя: {message.from_user.id}\n'
            f'Username: @{message.from_user.username}'
        )
        await bot.send_message(chat_id=-4554352254, text=group_message)
    logs_db.log_action(message.from_user.id, message.from_user.username, f"Команда /start")

@command_router.message(Command("userlogs"))
async def user_logs_command(message: types.Message):
    try:
        # Получаем ID пользователя из команды
        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            await message.reply("❌ Использование: `/userlogs <user_id>`", parse_mode='Markdown')
            return

        user_id = int(args[1])
        logs = logs_db.get_user_logs(user_id)  # Получаем логи через LogsDB

        if not logs:
            await message.reply(f"❌ Логи для пользователя {user_id} не найдены.")
            return

        # Формируем сообщение с логами
        logs_message = f"📋 *Активность пользователя {user_id}:*\n\n"
        for action, timestamp in logs:
            logs_message += f"🕒 {timestamp} — {action}\n"

        # Отправляем сообщение с логами
        await message.reply(logs_message, parse_mode='Markdown')

    except Exception as e:
        # Логирование ошибок, можно использовать LogsDB или стандартное логирование
        logs_db.log_action(message.from_user.id, message.from_user.username, f"Ошибка: {str(e)}")
        await message.reply(f"⚠️ Ошибка: {e}")

# def register_user_handlers(dp: Dispatcher) -> None:
#
#     dp.message_handler(cmd_start, commands=['start'])