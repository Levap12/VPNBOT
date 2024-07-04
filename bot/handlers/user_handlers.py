from aiogram import Router,Dispatcher,F,Bot
from bot.keyboards.user_keyboards import get_first_start_kb
from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from bot.utils import marzhapi
command_router = Router()


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

# def register_user_handlers(dp: Dispatcher) -> None:
#
#     dp.message_handler(cmd_start, commands=['start'])