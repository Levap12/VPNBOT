from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_first_start_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔌 Подключиться', callback_data='vless')]
    ])
    return ikb


def get_main_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🕹 Профиль', callback_data='profile'),InlineKeyboardButton(text='🛒 Купить VPN', callback_data='buyvpn')],
        [InlineKeyboardButton(text='🚀️ Подключится ', callback_data='vless')],
        [InlineKeyboardButton(text='⚙️ Поддержка', url='https://t.me/sd_kfu')]
    ])
    return ikb

def get_mainmenu_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]
    ])
    return ikb

def get_profile_kb() -> InlineKeyboardMarkup:
    # Профиль меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='⏳ Продлить подписку', callback_data='buyvpn')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return ikb

def get_buyvpn_kb() -> InlineKeyboardMarkup:
    # Купить ВПН меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='1 месяц', callback_data='buyvpn_1')],
         [InlineKeyboardButton(text='3 месяца', callback_data='buyvpn_3')],
         [InlineKeyboardButton(text='6 месяцев', callback_data='buyvpn_6')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])

    return ikb

def get_payment_kb(months: int, payment_url: str, crypto_payment_url: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🏦 Оплатить', url=payment_url)],
        [InlineKeyboardButton(text='💲 Оплатить криптовалютой', url=crypto_payment_url)],
        [InlineKeyboardButton(text='✅ Тестовая оплата', callback_data=f'test_payment_{months}')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])
    return ikb



def get_connect_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🧦 Outline', callback_data='outline'),InlineKeyboardButton(text='🛡 Vless', callback_data='vless')],
        [InlineKeyboardButton(text='Назад', callback_data='back_to_menu')]
    ])
    return ikb

def get_connected_kb() -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Быстрое подключение', callback_data='connect_web')],
                                                [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]])

    return ikb


def get_vless_con_kb() -> InlineKeyboardMarkup:
    # Главгвное меню

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Главное меню', callback_data='back_to_menu')]
    ])
    return ikb