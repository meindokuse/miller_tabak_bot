from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_products, get_aromas, get_low_stock_aromas, get_total_quantity, get_aromas_by_category


# Показать список товаров администратору с количеством ароматов
async def show_admin_products(message: types.Message, offset=0, edit_message_id=None):
    products = await get_products(offset)
    # Сортируем товары по имени (игнорируем регистр)
    products = sorted(products, key=lambda x: x[1].lower())

    keyboard = []
    for product in products:
        product_id, name, aroma_count = product
        keyboard.append(
            [InlineKeyboardButton(text=f"{name} ({aroma_count} ароматов)", callback_data=f"product_{product_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{offset - 10}")])
    if len(products) == 10:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")])
    keyboard.append([InlineKeyboardButton(text="⚠️ Ароматы < 251 гр", callback_data="low_stock")])
    keyboard.append([InlineKeyboardButton(text="📊 Инвентаризация", callback_data="inventory")])
    keyboard.append([
        InlineKeyboardButton(text="A категория", callback_data="category_A"),
        InlineKeyboardButton(text="B категория", callback_data="category_B"),
        InlineKeyboardButton(text="C категория", callback_data="category_C")
    ])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    text = "Товары:"
    if edit_message_id:
        await message.bot.edit_message_text(text=text, chat_id=str(message.chat.id), message_id=edit_message_id,
                                            reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


# Показать список ароматов для товара (админ)
async def show_admin_aromas(message: types.Message, product_id, offset=0, edit_message_id=None):
    aromas = await get_aromas(product_id, offset)
    # Сортируем ароматы по имени (игнорируем регистр)
    aromas = sorted(aromas, key=lambda x: x[1].lower())

    keyboard = []
    for aroma in aromas:
        aroma_id, aroma_name, quantity, category = aroma
        warning = "❗️" if quantity < 251 else ""
        keyboard.append([InlineKeyboardButton(text=f"{warning}{aroma_name}{warning} ({quantity} гр, {category})",
                                              callback_data=f"aroma_{aroma_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"aroma_prev_{product_id}_{offset - 10}")])
    if len(aromas) == 10:
        keyboard.append(
            [InlineKeyboardButton(text="Вперед ➡️", callback_data=f"aroma_next_{product_id}_{offset + 10}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить аромат", callback_data=f"add_aroma_{product_id}")])
    keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data="main")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    text = "Управление ароматами:"
    if edit_message_id:
        await message.bot.edit_message_text(text=text, chat_id=str(message.chat.id), message_id=edit_message_id,
                                            reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


# Показать список ароматов с количеством < 251 гр
async def show_low_stock_aromas(message: types.Message, edit_message_id=None):
    aromas = await get_low_stock_aromas()
    if not aromas:
        text = "Нет ароматов с количеством менее 251 гр."
    else:
        # Группируем ароматы по товарам
        products = {}
        for product_name, aroma_name, quantity, category in aromas:
            if product_name not in products:
                products[product_name] = []
            products[product_name].append((aroma_name, quantity, category))

        # Сортируем товары по имени (игнорируем регистр)
        sorted_products = sorted(products.items(), key=lambda x: x[0].lower())

        # Форматируем текст
        text = "⚠️ Ароматы с количеством < 251 гр:\n\n"
        for product_name, aroma_list in sorted_products:
            # Сортируем ароматы внутри каждого товара (игнорируем регистр)
            sorted_aromas = sorted(aroma_list, key=lambda x: x[0].lower())
            aroma_texts = [f"  • {aroma_name} ({quantity} гр, {category})" for aroma_name, quantity, category in
                           sorted_aromas]
            text += f"*{product_name}*:\n" + "\n".join(aroma_texts) + "\n\n"
        text = text.strip()

    keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        await message.bot.edit_message_text(text=text, chat_id=str(message.chat.id), message_id=edit_message_id,
                                            reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")


# Показать ароматы по категории (A, B, C)
async def show_aromas_by_category(message: types.Message, category, edit_message_id=None):
    aromas = await get_aromas_by_category(category)
    if not aromas:
        text = f"Нет ароматов в категории {category}."
    else:
        # Группируем ароматы по товарам
        products = {}
        for product_name, aroma_name, quantity, category in aromas:
            if product_name not in products:
                products[product_name] = []
            products[product_name].append((aroma_name, quantity))

        # Сортируем товары по имени (игнорируем регистр)
        sorted_products = sorted(products.items(), key=lambda x: x[0].lower())

        # Форматируем текст
        text = f"Ароматы категории {category}:\n\n"
        for product_name, aroma_list in sorted_products:
            # Сортируем ароматы внутри каждого товара (игнорируем регистр)
            sorted_aromas = sorted(aroma_list, key=lambda x: x[0].lower())
            aroma_texts = [f"  • {aroma_name} ({quantity} гр)" for aroma_name, quantity in sorted_aromas]
            text += f"*{product_name}*:\n" + "\n".join(aroma_texts) + "\n\n"
        text = text.strip()

    keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        await message.bot.edit_message_text(text=text, chat_id=str(message.chat.id), message_id=edit_message_id,
                                            reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")


# Показать общее количество грамм (инвентаризация)
async def show_inventory(message: types.Message, edit_message_id=None):
    total_quantity = await get_total_quantity()
    text = f"📊 Инвентаризация:\nОбщее количество: {total_quantity} гр"
    keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        await message.bot.edit_message_text(text=text, chat_id=str(message.chat.id), message_id=edit_message_id,
                                            reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)