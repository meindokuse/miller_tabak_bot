from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_products, get_flavors


# Показать список товаров администратору с количеством вкусов
async def show_admin_products(message: types.Message, offset=0):
    products = await get_products(offset)
    keyboard = []
    for product in products:
        product_id, name, flavor_count = product
        keyboard.append(
            [InlineKeyboardButton(text=f"{name} ({flavor_count} вкусов)", callback_data=f"product_{product_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{offset - 10}")])
    if len(products) == 10:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Товары:", reply_markup=reply_markup)


# Показать список вкусов для товара (админ)
async def show_admin_flavors(message: types.Message, product_id, offset=0):
    flavors = await get_flavors(product_id, offset)
    keyboard = []
    for flavor in flavors:
        flavor_id, flavor_name, quantity, price = flavor
        # Добавляем "!" если количество < 500 гр
        warning = "❗️" if quantity < 500 else ""
        keyboard.append([InlineKeyboardButton(text=f"{warning} {flavor_name} {warning} ({quantity} гр, {price} руб.)",
                                              callback_data=f"flavor_{flavor_id}")])

    if offset > 0:
        keyboard.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"flavor_prev_{product_id}_{offset - 10}")])
    if len(flavors) == 10:
        keyboard.append(
            [InlineKeyboardButton(text="Вперед ➡️", callback_data=f"flavor_next_{product_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить вкус", callback_data=f"add_flavor_{product_id}")])
    keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data="main")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Управление вкусами:", reply_markup=reply_markup)