import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from database import (get_product_by_id, get_aroma_by_id, update_aroma_quantity, update_aroma_category,
                      update_product_name, init_db, add_product, add_aroma, delete_product_db, delete_aroma_db,
                      get_aromas)
from service import show_admin_products, show_admin_aromas, show_low_stock_aromas, show_inventory, \
    show_aromas_by_category

TRUSTED_CHAT_IDS = [1082039395, 444627449, 883974728]  # Список доверенных chat_id

bot = Bot(token=os.getenv("TOKEN_S"))
dp = Dispatcher()


class AdminStates(StatesGroup):
    EnterNewProductName = State()
    EnterNewAromaName = State()
    EnterNewAromaQuantity = State()
    EnterNewAromaCategory = State()
    EnterManualQuantity = State()
    EnterNewProductNameEdit = State()
    EnterNewAromaCategoryEdit = State()
    EnterSupplyData = State()
    EnterBulkAddAromas = State()
    ConfirmDeleteProduct = State()  # Состояние для подтверждения удаления товара
    ConfirmDeleteAroma = State()   # Состояние для подтверждения удаления аромата


# Проверка доверенного chat_id
def is_trusted_user(chat_id: int) -> bool:
    return chat_id in TRUSTED_CHAT_IDS


@dp.message(CommandStart())
async def cmd_start(message: Message):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    await init_db()
    await show_admin_products(message)


@dp.callback_query(lambda c: c.data == "main")
async def back_to_main(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("product_"))
async def admin_product(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[1])
    product = await get_product_by_id(product_id)
    keyboard = [
        [InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать название", callback_data=f"edit_product_name_{product_id}")],
        [InlineKeyboardButton(text="Ароматы", callback_data=f"show_aromas_{product_id}")],
        [InlineKeyboardButton(text="Назад к товарам", callback_data="main")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text=f"Товар: {product[1]}",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("show_aromas_"))
async def admin_show_aromas(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[2])
    await bot.answer_callback_query(callback.id)
    await show_admin_aromas(callback.message, product_id, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("aroma_next_"))
async def admin_aroma_next(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_admin_aromas(callback.message, product_id, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("aroma_prev_"))
async def admin_aroma_prev(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_admin_aromas(callback.message, product_id, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("aroma_"))
async def admin_aroma(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    aroma_id = int(callback.data.split("_")[1])
    aroma = await get_aroma_by_id(aroma_id)
    keyboard = [
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_aroma_{aroma_id}")],
        [InlineKeyboardButton(text="✏️ Изменить количество", callback_data=f"change_quantity_{aroma_id}")],
        [InlineKeyboardButton(text="📝 Изменить категорию", callback_data=f"edit_aroma_category_{aroma_id}")],
        [InlineKeyboardButton(text="Назад к ароматам", callback_data=f"show_aromas_{aroma[1]}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text=f"Аромат: {aroma[2]}\nКоличество: {aroma[3]} гр\nКатегория: {aroma[4]}",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("change_quantity_"))
async def admin_change_quantity(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    aroma_id = int(callback.data.split("_")[2])
    aroma = await get_aroma_by_id(aroma_id)
    keyboard = [
        [InlineKeyboardButton(text="➕ +100 гр", callback_data=f"increase_{aroma_id}_100")],
        [InlineKeyboardButton(text="➖ -100 гр", callback_data=f"decrease_{aroma_id}_100")],
        [InlineKeyboardButton(text="➕ +250 гр", callback_data=f"increase_{aroma_id}_250")],
        [InlineKeyboardButton(text="➖ -250 гр", callback_data=f"decrease_{aroma_id}_250")],
        [InlineKeyboardButton(text="➕ +50 гр", callback_data=f"increase_{aroma_id}_50")],
        [InlineKeyboardButton(text="➖ -50 гр", callback_data=f"decrease_{aroma_id}_50")],
        [InlineKeyboardButton(text="📝 Ввести вручную", callback_data=f"manual_{aroma_id}")],
        [InlineKeyboardButton(text="Назад к ароматам", callback_data=f"show_aromas_{aroma[1]}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text=f"Текущее количество: {aroma[3]} гр",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id,
        reply_markup=reply_markup
    )


@dp.callback_query(lambda c: c.data.startswith("increase_"))
async def admin_increase(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    increase = int(callback.data.split("_")[2])
    aroma_id = int(callback.data.split("_")[1])
    aroma = await get_aroma_by_id(aroma_id)
    new_quantity = aroma[3] + increase
    await update_aroma_quantity(aroma_id, new_quantity)
    await bot.answer_callback_query(callback.id)
    await show_admin_aromas(callback.message, aroma[1], edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("decrease_"))
async def admin_decrease(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    decrease = int(callback.data.split("_")[2])
    aroma_id = int(callback.data.split("_")[1])
    aroma = await get_aroma_by_id(aroma_id)
    new_quantity = max(0, aroma[3] - decrease)
    await update_aroma_quantity(aroma_id, new_quantity)
    await bot.answer_callback_query(callback.id)
    await show_admin_aromas(callback.message, aroma[1], edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("manual_"))
async def admin_manual(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    aroma_id = int(callback.data.split("_")[1])
    await state.set_state(AdminStates.EnterManualQuantity)
    await state.update_data(aroma_id=aroma_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите новое количество (в граммах):",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("edit_product_name_"))
async def admin_edit_product_name(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[3])
    await state.set_state(AdminStates.EnterNewProductNameEdit)
    await state.update_data(product_id=product_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите новое название товара:",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("edit_aroma_category_"))
async def admin_edit_aroma_category(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    aroma_id = int(callback.data.split("_")[3])
    await state.set_state(AdminStates.EnterNewAromaCategoryEdit)
    await state.update_data(aroma_id=aroma_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите новую категорию аромата (A, B или C):",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("prev_"))
async def admin_prev(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    offset = int(callback.data.split("_")[1])
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("next_"))
async def admin_next(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    offset = int(callback.data.split("_")[1])
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == "add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    await state.set_state(AdminStates.EnterNewProductName)
    await state.update_data(message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите название товара:",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("add_aroma_"))
async def admin_add_aroma(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[2])
    await state.set_state(AdminStates.EnterNewAromaName)
    await state.update_data(product_id=product_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите название аромата:",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.callback_query(lambda c: c.data.startswith("delete_product_"))
async def admin_delete_product(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[2])
    product = await get_product_by_id(product_id)
    keyboard = [
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_delete_product_{product_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data="main")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text=f"Вы уверены, что хотите удалить товар '{product[1]}'?",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id,
        reply_markup=reply_markup
    )
    await state.set_state(AdminStates.ConfirmDeleteProduct)
    await state.update_data(product_id=product_id, message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("confirm_delete_product_"))
async def confirm_delete_product(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[3])
    await delete_product_db(product_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Товар успешно удалён!",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )
    await state.clear()
    await asyncio.sleep(1)
    await show_admin_products(callback.message, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("delete_aroma_"))
async def admin_delete_aroma(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    aroma_id = int(callback.data.split("_")[2])
    aroma = await get_aroma_by_id(aroma_id)
    keyboard = [
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_delete_aroma_{aroma_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data=f"show_aromas_{aroma[1]}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text=f"Вы уверены, что хотите удалить аромат '{aroma[2]}'?",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id,
        reply_markup=reply_markup
    )
    await state.set_state(AdminStates.ConfirmDeleteAroma)
    await state.update_data(aroma_id=aroma_id, product_id=aroma[1], message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("confirm_delete_aroma_"))
async def confirm_delete_aroma(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    aroma_id = int(callback.data.split("_")[3])
    product_id = data['product_id']
    await delete_aroma_db(aroma_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Аромат успешно удалён!",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )
    await state.clear()
    await asyncio.sleep(1)
    await show_admin_aromas(callback.message, product_id, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("low_stock_prev_"))
async def admin_low_stock_prev(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    offset = int(callback.data.split("_")[3])
    await bot.answer_callback_query(callback.id)
    await show_low_stock_aromas(callback.message, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("low_stock_next_"))
async def admin_low_stock_next(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    offset = int(callback.data.split("_")[3])
    await bot.answer_callback_query(callback.id)
    await show_low_stock_aromas(callback.message, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == "low_stock")
async def admin_low_stock(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    await bot.answer_callback_query(callback.id)
    await show_low_stock_aromas(callback.message, offset=0, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data == "inventory")
async def admin_inventory(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    await bot.answer_callback_query(callback.id)
    await show_inventory(callback.message, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("category_") and ("_prev_") in c.data)
async def admin_category_prev(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    parts = callback.data.split("_")
    category = parts[1]
    offset = int(parts[3])
    await bot.answer_callback_query(callback.id)
    await show_aromas_by_category(callback.message, category, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("category_") and ("_next_") in c.data)
async def admin_category_next(callback: CallbackQuery):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    parts = callback.data.split("_")
    category = parts[1]
    offset = int(parts[3])
    await bot.answer_callback_query(callback.id)
    await show_aromas_by_category(callback.message, category, offset, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data in ["category_A", "category_B", "category_C"])
async def admin_category(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    category = callback.data.split("_")[1]
    await bot.answer_callback_query(callback.id)
    await show_aromas_by_category(callback.message, category, offset=0, edit_message_id=callback.message.message_id)


@dp.callback_query(lambda c: c.data.startswith("supply_"))
async def admin_supply(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[1])
    await state.set_state(AdminStates.EnterSupplyData)
    await state.update_data(product_id=product_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите данные поставки в формате:\n(название аромата) (кол-во грамм)",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.message(AdminStates.EnterManualQuantity)
async def process_manual_quantity(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    aroma_id = data['aroma_id']
    message_id = data['message_id']
    new_quantity = int(message.text)
    await update_aroma_quantity(aroma_id, new_quantity)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await show_admin_aromas(message, (await get_aroma_by_id(aroma_id))[1], edit_message_id=message_id)
    await state.clear()


@dp.message(AdminStates.EnterNewProductName)
async def process_product_name(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    message_id = data['message_id']
    product_id = await add_product(message.text)
    await state.update_data(product_id=product_id)
    await state.set_state(AdminStates.EnterNewAromaName)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await bot.edit_message_text(
        text="Введите название первого аромата:",
        chat_id=str(message.chat.id),
        message_id=message_id
    )


@dp.message(AdminStates.EnterNewAromaName)
async def process_aroma_name(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    message_id = data['message_id']
    await state.update_data(aroma_name=message.text)
    await state.set_state(AdminStates.EnterNewAromaQuantity)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await bot.edit_message_text(
        text="Введите количество (в граммах):",
        chat_id=str(message.chat.id),
        message_id=message_id
    )


@dp.message(AdminStates.EnterNewAromaQuantity)
async def process_aroma_quantity(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    message_id = data['message_id']
    try:
        quantity = int(message.text)
        if quantity < 0:
            raise ValueError
        await state.update_data(quantity=quantity)
        await state.set_state(AdminStates.EnterNewAromaCategory)
        await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
        await bot.edit_message_text(
            text="Введите категорию (A, B или C):",
            chat_id=str(message.chat.id),
            message_id=message_id
        )
    except ValueError:
        await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
        await bot.edit_message_text(
            text="Введите корректное число (например, 100):",
            chat_id=str(message.chat.id),
            message_id=message_id
        )


@dp.message(AdminStates.EnterNewAromaCategory)
async def process_aroma_category(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    message_id = data['message_id']
    category = message.text.upper()
    if category not in ['A', 'B', 'C']:
        await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
        await bot.edit_message_text(
            text="Введите корректную категорию (A, B или C):",
            chat_id=str(message.chat.id),
            message_id=message_id
        )
        return
    await add_aroma(data['product_id'], data['aroma_name'], data['quantity'], category)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await show_admin_aromas(message, data['product_id'], edit_message_id=message_id)
    await state.clear()


@dp.message(AdminStates.EnterNewProductNameEdit)
async def process_product_name_edit(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    product_id = data['product_id']
    message_id = data['message_id']
    new_name = message.text
    await update_product_name(product_id, new_name)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await show_admin_products(message, edit_message_id=message_id)
    await state.clear()


@dp.message(AdminStates.EnterNewAromaCategoryEdit)
async def process_aroma_category_edit(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    aroma_id = data['aroma_id']
    message_id = data['message_id']
    new_category = message.text.upper()
    if new_category not in ['A', 'B', 'C']:
        await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
        await bot.edit_message_text(
            text="Введите корректную категорию (A, B или C):",
            chat_id=str(message.chat.id),
            message_id=message_id
        )
        return
    await update_aroma_category(aroma_id, new_category)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await show_admin_aromas(message, (await get_aroma_by_id(aroma_id))[1], edit_message_id=message_id)
    await state.clear()


@dp.message(AdminStates.EnterSupplyData)
async def process_supply_data(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    product_id = data['product_id']
    message_id = data['message_id']
    aromas = await get_aromas(product_id, offset=0, limit=9999)
    aroma_dict = {aroma[1].lower(): (aroma[0], int(aroma[2])) for aroma in aromas}
    lines = message.text.strip().split('\n')
    updated_aromas = []
    errors = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            errors.append(f"Неверный формат строки: {line}")
            continue
        quantity_str = parts[-1]
        aroma_name = " ".join(parts[:-1]).lower()
        try:
            quantity_to_add = int(quantity_str)
            if quantity_to_add < 0:
                errors.append(f"Количество не может быть отрицательным: {line}")
                continue
        except ValueError:
            errors.append(f"Неверное количество в строке: {line}")
            continue
        if aroma_name in aroma_dict:
            aroma_id, current_quantity = aroma_dict[aroma_name]
            new_quantity = current_quantity + quantity_to_add
            await update_aroma_quantity(aroma_id, new_quantity)
            updated_aromas.append(f"{aroma_name} (+{quantity_to_add} гр, теперь {new_quantity} гр)")
        else:
            errors.append(f"Аромат не найден: {aroma_name}")
    response_text = "📦 Результат поставки:\n\n"
    if updated_aromas:
        response_text += "Обновлены:\n" + "\n".join(updated_aromas) + "\n\n"
    if errors:
        response_text += "Ошибки:\n" + "\n".join(errors)
    else:
        response_text += "Все ароматы успешно обновлены!"
    keyboard = [[InlineKeyboardButton(text="К списку ароматов", callback_data=f"show_aromas_{product_id}")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await bot.edit_message_text(
        text=response_text,
        chat_id=str(message.chat.id),
        message_id=message_id,
        reply_markup=reply_markup
    )
    await state.clear()


@dp.callback_query(lambda c: c.data.startswith("bulk_add_aromas_"))
async def admin_bulk_add_aromas(callback: CallbackQuery, state: FSMContext):
    if not is_trusted_user(callback.from_user.id):
        await bot.send_message(str(callback.from_user.id), "Доступ только для доверенных администраторов.")
        return
    product_id = int(callback.data.split("_")[3])
    await state.set_state(AdminStates.EnterBulkAddAromas)
    await state.update_data(product_id=product_id, message_id=callback.message.message_id)
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        text="Введите список новых ароматов в формате:\n(название) (кол-во грамм) (категория)\nПример:\nклубника 1000 A\nяблоко 1999 B\nкиви 800 C\nвиноград 900 A",
        chat_id=str(callback.message.chat.id),
        message_id=callback.message.message_id
    )


@dp.message(AdminStates.EnterBulkAddAromas)
async def process_bulk_add_aromas(message: Message, state: FSMContext):
    if not is_trusted_user(message.from_user.id):
        await message.answer("Доступ только для доверенных администраторов.")
        return
    data = await state.get_data()
    product_id = data['product_id']
    message_id = data['message_id']
    existing_aromas = await get_aromas(product_id, offset=0, limit=9999)
    existing_aroma_names = {aroma[1].lower() for aroma in existing_aromas}
    lines = message.text.strip().split('\n')
    added_aromas = []
    errors = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            errors.append(f"Неверный формат строки: {line} (ожидается: название количество категория)")
            continue
        category = parts[-1].upper()
        quantity_str = parts[-2]
        aroma_name = " ".join(parts[:-2])
        if category not in ['A', 'B', 'C']:
            errors.append(f"Неверная категория в строке: {line} (должно быть A, B или C)")
            continue
        try:
            quantity = int(quantity_str)
            if quantity < 0:
                errors.append(f"Количество не может быть отрицательным: {line}")
                continue
        except ValueError:
            errors.append(f"Неверное количество в строке: {line}")
            continue
        if aroma_name.lower() in existing_aroma_names:
            errors.append(f"Аромат уже существует: {aroma_name}")
            continue
        await add_aroma(product_id, aroma_name, quantity, category)
        added_aromas.append(f"{aroma_name} ({quantity} гр, {category})")
        existing_aroma_names.add(aroma_name.lower())
    response_text = "📋 Результат добавления ароматов:\n\n"
    if added_aromas:
        response_text += "Добавлены:\n" + "\n".join(added_aromas) + "\n\n"
    if errors:
        response_text += "Ошибки:\n" + "\n".join(errors)
    else:
        response_text += "Все ароматы успешно добавлены!"
    keyboard = [[InlineKeyboardButton(text="К списку ароматов", callback_data=f"show_aromas_{product_id}")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.delete_message(chat_id=str(message.chat.id), message_id=message.message_id)
    await bot.edit_message_text(
        text=response_text,
        chat_id=str(message.chat.id),
        message_id=message_id,
        reply_markup=reply_markup
    )
    await state.clear()


async def on_startup(dp):
    await init_db()


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot, on_startup=on_startup, skip_updates=True))