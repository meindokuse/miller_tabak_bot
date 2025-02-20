from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_products


async def show_user_products(message: types.Message, offset=0):
    products = await get_products(offset)
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(text = product[1], callback_data=f"product_{product[0]}")])
    # Пагинация
    if offset > 0:
        keyboard.append([InlineKeyboardButton(text = "⬅️ Назад", callback_data=f"prev_{offset-20}")])
    if len(products) == 20:
        keyboard.append([InlineKeyboardButton(text = "Вперед ➡️", callback_data=f"next_{offset+20}")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выберите товар:", reply_markup=reply_markup)

# Показать товары администратору
async def show_admin_products(message: types.Message, offset=0):
    products = await get_products(offset)
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(text = product[1], callback_data=f"admin_product_{product[0]}")])
    # Пагинация и кнопка добавления
    if offset > 0:
        keyboard.append([InlineKeyboardButton(text = "⬅️ Назад", callback_data=f"admin_prev_{offset-20}")])
    if len(products) == 20:
        keyboard.append([InlineKeyboardButton(text = "Вперед ➡️", callback_data=f"admin_next_{offset+20}")])
    keyboard.append([InlineKeyboardButton(text = "➕ Добавить новый товар", callback_data="add_new_product")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выберите товар:", reply_markup=reply_markup)
