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
bot = Bot(token=token)#'7464437998:AAHovjFWytYVAwi8_qk2RnfyIXh2HxhM0pM')

@command_router.message(CommandStart())
async def cmd_start(message: Message):
    main_menu = f'🖖 Привет {message.from_user.first_name}!' \
                '\nЯ — Nock VPN бот.' \
                '\nЯ подключу вас к VPN за пару простых шагов.' \
                '\nПопробуй бесплатно 72 часа самый быстрый VPN в Европе.' \
                '\nЖми 🔌Подключиться ниже в меню и я помогу настроить VPN на любом устройстве за 2 минуты.\n'
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
    await message.answer(
        text=main_menu,
        reply_markup=get_first_start_kb(), parse_mode='HTML'
    )

# def register_user_handlers(dp: Dispatcher) -> None:
#
#     dp.message_handler(cmd_start, commands=['start'])