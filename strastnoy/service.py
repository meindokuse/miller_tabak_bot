from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import get_products, get_aromas, get_low_stock_aromas, get_total_quantity, get_aromas_by_category, \
    get_low_stock_aromas_count, get_aromas_count, get_products_count, get_aromas_by_category_count


async def show_admin_products(message: types.Message, offset=0, edit_message_id=None):
    limit = 10
    products = await get_products(offset, limit)
    total_products = await get_products_count()

    keyboard = []
    for product in products:
        product_id, name, aroma_count = product
        keyboard.append(
            [InlineKeyboardButton(text=f"{name} ({aroma_count} ароматов)", callback_data=f"product_{product_id}")])

    if offset > 0:
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_{offset - limit}")])
    if offset + limit < total_products:
        keyboard.append([InlineKeyboardButton(text="Вперед ➡️", callback_data=f"next_{offset + limit}")])
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
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=str(message.chat.id),
                message_id=edit_message_id,
                reply_markup=reply_markup
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return  # Игнорируем, если сообщение не изменилось
            raise  # Если другая ошибка, пробрасываем её
        except Exception:
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


async def show_admin_aromas(message: types.Message, product_id, offset=0, edit_message_id=None):
    limit = 10
    aromas = await get_aromas(product_id, offset, limit)
    total_aromas = await get_aromas_count(product_id)

    keyboard = []
    for aroma in aromas:
        aroma_id, aroma_name, quantity, category = aroma
        warning = "❗️" if quantity < 251 else ""
        keyboard.append([InlineKeyboardButton(text=f"{warning}{aroma_name}{warning} ({quantity} гр, {category})",
                                              callback_data=f"aroma_{aroma_id}")])

    if offset > 0:
        keyboard.append(
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"aroma_prev_{product_id}_{offset - limit}")])
    if offset + limit < total_aromas:
        keyboard.append(
            [InlineKeyboardButton(text="Вперед ➡️", callback_data=f"aroma_next_{product_id}_{offset + limit}")])
    keyboard.append([InlineKeyboardButton(text="➕ Добавить аромат", callback_data=f"add_aroma_{product_id}")])
    keyboard.append(
        [InlineKeyboardButton(text="📋 Добавить ароматы списком", callback_data=f"bulk_add_aromas_{product_id}")])
    keyboard.append([InlineKeyboardButton(text="📦 Поставка", callback_data=f"supply_{product_id}")])
    keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data="main")])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    text = "Управление ароматами:"

    if edit_message_id:
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=str(message.chat.id),
                message_id=edit_message_id,
                reply_markup=reply_markup
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            raise
        except Exception:
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)


async def show_low_stock_aromas(message: types.Message, offset=0, edit_message_id=None):
    limit = 10
    aromas = await get_low_stock_aromas(offset, limit)
    total_aromas = await get_low_stock_aromas_count()

    if not aromas:
        text = "Нет ароматов с количеством менее 251 гр."
        keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        text = "⚠️ Ароматы с количеством < 251 гр:\n\n"
        current_product = None
        for product_name, aroma_name, quantity, category in aromas:
            if product_name != current_product:
                if current_product is not None:
                    text += "\n"
                text += f"*{product_name}*:\n"
                current_product = product_name
            text += f"  • {aroma_name} ({quantity} гр, {category})\n"
        text = text.strip()

        keyboard = []
        pagination_row = []
        if offset > 0:
            pagination_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"low_stock_prev_{offset - limit}"))
        if offset + limit < total_aromas:
            pagination_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"low_stock_next_{offset + limit}"))
        if pagination_row:
            keyboard.append(pagination_row)
        keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data="main")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=str(message.chat.id),
                message_id=edit_message_id,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            raise
        except Exception:
            await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_aromas_by_category(message: types.Message, category, offset=0, edit_message_id=None):
    limit = 10
    aromas = await get_aromas_by_category(category, offset, limit)
    total_aromas = await get_aromas_by_category_count(category)

    if not aromas:
        text = f"Нет ароматов в категории {category}."
        keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        text = f"Ароматы категории {category}:\n\n"
        current_product = None
        for product_name, aroma_name, quantity, category in aromas:
            if product_name != current_product:
                if current_product is not None:
                    text += "\n"
                text += f"*{product_name}*:\n"
                current_product = product_name
            text += f"  • {aroma_name} ({quantity} гр)\n"
        text = text.strip()

        keyboard = []
        pagination_row = []
        if offset > 0:
            pagination_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"category_{category}_prev_{offset - limit}"))
        if offset + limit < total_aromas:
            pagination_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"category_{category}_next_{offset + limit}"))
        if pagination_row:
            keyboard.append(pagination_row)
        keyboard.append([InlineKeyboardButton(text="Назад к товарам", callback_data="main")])
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=str(message.chat.id),
                message_id=edit_message_id,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            raise
        except Exception:
            await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")


async def show_inventory(message: types.Message, edit_message_id=None):
    total_quantity = await get_total_quantity()
    text = f"📊 Инвентаризация:\nОбщее количество: {total_quantity} гр"
    keyboard = [[InlineKeyboardButton(text="Назад к товарам", callback_data="main")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if edit_message_id:
        try:
            await message.bot.edit_message_text(
                text=text,
                chat_id=str(message.chat.id),
                message_id=edit_message_id,
                reply_markup=reply_markup
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                return
            raise
        except Exception:
            await message.answer(text, reply_markup=reply_markup)
    else:
        await message.answer(text, reply_markup=reply_markup)