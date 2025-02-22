from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_locations, get_products, get_flavors


# Показать список магазинов
async def show_locations(message: types.Message):
    locations = await get_locations()
    keyboard = []
    for loc in locations:
        loc_id, name = loc
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"location_{loc_id}")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выберите магазин:", reply_markup=reply_markup)


# Показать список товаров пользователю
async def show_user_products(message: types.Message, location_id, offset=0):
    products = await get_products(location_id, offset)
    keyboard = []
    for product in products:
        product_id, name = product
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"product_{location_id}_{product_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{location_id}_{offset - 10}")])
    if len(products) == 10:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{location_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="К выбору магазина", callback_data="locations")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(f"Товары в магазине {location_id}:", reply_markup=reply_markup)


# Показать список вкусов для товара (пользователь)
async def show_user_flavors(message: types.Message, location_id, product_id, offset=0):
    flavors = await get_flavors(product_id, offset)
    keyboard = []
    for flavor in flavors:
        flavor_id, flavor_name, quantity, price = flavor
        keyboard.append([InlineKeyboardButton(text=flavor_name, callback_data=f"flavor_{location_id}_{flavor_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад",
                                              callback_data=f"flavor_prev_{location_id}_{product_id}_{offset - 10}")])
    if len(flavors) == 10:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️",
                                              callback_data=f"flavor_next_{location_id}_{product_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data=f"location_{location_id}")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Выберите вкус:", reply_markup=reply_markup)


# Показать список товаров администратору
async def show_admin_products(message: types.Message, location_id, offset=0):
    products = await get_products(location_id, offset)
    keyboard = []
    for product in products:
        product_id, name = product
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"admin_product_{location_id}_{product_id}")])

    if offset > 0:
        keyboard.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_prev_{location_id}_{offset - 10}")])
    if len(products) == 10:
        keyboard.append(
            [InlineKeyboardButton(text="Вперед ➡️", callback_data=f"admin_next_{location_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить товар", callback_data=f"add_product_{location_id}")])
    keyboard.append([InlineKeyboardButton(text="К выбору магазина", callback_data="locations")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(f"Товары в магазине {location_id} (админ):", reply_markup=reply_markup)


# Показать список вкусов для товара (админ)
async def show_admin_flavors(message: types.Message, location_id, product_id, offset=0):
    flavors = await get_flavors(product_id, offset)
    keyboard = []
    for flavor in flavors:
        flavor_id, flavor_name, quantity, price = flavor
        keyboard.append([InlineKeyboardButton(text=f"{flavor_name} ({quantity} шт.)",
                                              callback_data=f"admin_flavor_{location_id}_{flavor_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад",
                                              callback_data=f"admin_flavor_prev_{location_id}_{product_id}_{offset - 10}")])
    if len(flavors) == 10:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️",
                                              callback_data=f"admin_flavor_next_{location_id}_{product_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить вкус", callback_data=f"add_flavor_{product_id}")])
    keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data=f"location_{location_id}")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("Управление вкусами (админ):", reply_markup=reply_markup)