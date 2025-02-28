import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from database import (get_product_by_id, get_flavor_by_id, update_flavor_quantity, update_flavor_price,
                     update_product_name, init_db, add_product, add_flavor, delete_product_db, delete_flavor_db)
from service import show_locations, show_user_products, show_user_flavors, show_admin_products, show_admin_flavors

API_TOKEN = '8037910201:AAHEwbfNG4feas1J4N71inZAO0l-B8WZS6o'
ADMIN_CHAT_ID = 1082039395

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class AdminStates(StatesGroup):
    EnterNewProductName = State()
    EnterNewFlavorName = State()
    EnterNewFlavorQuantity = State()
    EnterNewFlavorPrice = State()
    EnterManualQuantity = State()
    EnterNewProductNameEdit = State()
    EnterNewFlavorPriceEdit = State()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await init_db()
    await show_locations(message)

# Пользовательские callback
@dp.callback_query(lambda c: c.data.startswith("location_") and c.from_user.id != ADMIN_CHAT_ID)
async def user_location(callback: CallbackQuery):
    location_id = int(callback.data.split("_")[1])
    await bot.answer_callback_query(callback.id)
    await show_user_products(callback.message, location_id)

@dp.callback_query(lambda c: c.data.startswith("product_"))
async def user_product(callback: CallbackQuery):
    location_id, product_id = map(int, callback.data.split("_")[1:])
    await bot.answer_callback_query(callback.id)
    await show_user_flavors(callback.message, location_id, product_id)

@dp.callback_query(lambda c: c.data.startswith("flavor_"))
async def user_flavor(callback: CallbackQuery):
    location_id, flavor_id = map(int, callback.data.split("_")[1:])
    flavor = await get_flavor_by_id(flavor_id)
    keyboard = [[InlineKeyboardButton(text="Назад к вкусам", callback_data=f"product_{location_id}_{flavor[1]}")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id,
                           f"Название: {flavor[2]}\nКоличество: {flavor[3]}\nЦена: {flavor[4]} руб.",
                           reply_markup=reply_markup)

@dp.callback_query(lambda c: c.data.startswith("prev_"))
async def user_prev(callback: CallbackQuery):
    location_id, offset = map(int, callback.data.split("_")[1:])
    await bot.answer_callback_query(callback.id)
    await show_user_products(callback.message, location_id, offset)

@dp.callback_query(lambda c: c.data.startswith("next_"))
async def user_next(callback: CallbackQuery):
    location_id, offset = map(int, callback.data.split("_")[1:])
    await bot.answer_callback_query(callback.id)
    await show_user_products(callback.message, location_id, offset)

@dp.callback_query(lambda c: c.data.startswith("flavor_prev_"))
async def user_flavor_prev(callback: CallbackQuery):
    location_id, product_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_user_flavors(callback.message, location_id, product_id, offset)

@dp.callback_query(lambda c: c.data.startswith("flavor_next_"))
async def user_flavor_next(callback: CallbackQuery):
    location_id, product_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_user_flavors(callback.message, location_id, product_id, offset)

# Админские callback
@dp.callback_query(lambda c: c.data == "locations")
async def back_to_locations(callback: CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await show_locations(callback.message)

@dp.callback_query(lambda c: c.data.startswith("location_") and c.from_user.id == ADMIN_CHAT_ID)
async def admin_location(callback: CallbackQuery):
    location_id = int(callback.data.split("_")[1])
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, location_id)

@dp.callback_query(lambda c: c.data.startswith("admin_product_"))
async def admin_product(callback: CallbackQuery):
    location_id, product_id = map(int, callback.data.split("_")[2:])
    product = await get_product_by_id(product_id)
    keyboard = [
        [InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"delete_product_{product_id}")],
        [InlineKeyboardButton(text="✏️ Редактировать название", callback_data=f"edit_product_name_{product_id}")],
        [InlineKeyboardButton(text="Вкусы", callback_data=f"show_flavors_{location_id}_{product_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, f"Товар: {product[2]}", reply_markup=reply_markup)

@dp.callback_query(lambda c: c.data.startswith("show_flavors_"))
async def admin_show_flavors(callback: CallbackQuery):
    location_id, product_id = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_admin_flavors(callback.message, location_id, product_id)

@dp.callback_query(lambda c: c.data.startswith("admin_flavor_"))
async def admin_flavor(callback: CallbackQuery):
    location_id, flavor_id = map(int, callback.data.split("_")[2:])
    flavor = await get_flavor_by_id(flavor_id)
    keyboard = [
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_flavor_{flavor_id}")],
        [InlineKeyboardButton(text="✏️ Изменить количество", callback_data=f"change_quantity_{flavor_id}")],
        [InlineKeyboardButton(text="💰 Изменить цену", callback_data=f"edit_flavor_price_{flavor_id}")],
        [InlineKeyboardButton(text="Назад к вкусам", callback_data=f"show_flavors_{location_id}_{flavor[1]}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id,
                           f"Вкус: {flavor[2]}\nКоличество: {flavor[3]}\nЦена: {flavor[4]} руб.",
                           reply_markup=reply_markup)

@dp.callback_query(lambda c: c.data.startswith("change_quantity_"))
async def admin_change_quantity(callback: CallbackQuery):
    flavor_id = int(callback.data.split("_")[2])
    flavor = await get_flavor_by_id(flavor_id)
    keyboard = [
        [InlineKeyboardButton(text="➕ +1", callback_data=f"increase_{flavor_id}")],
        [InlineKeyboardButton(text="➖ -1", callback_data=f"decrease_{flavor_id}")],
        [InlineKeyboardButton(text="📝 Ввести вручную", callback_data=f"manual_{flavor_id}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"show_flavors_{callback.message.chat.id}_{flavor[1]}")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, f"Текущее количество: {flavor[3]}", reply_markup=reply_markup)

@dp.callback_query(lambda c: c.data.startswith("increase_"))
async def admin_increase(callback: CallbackQuery):
    flavor_id = int(callback.data.split("_")[1])
    flavor = await get_flavor_by_id(flavor_id)
    new_quantity = flavor[3] + 1
    await update_flavor_quantity(flavor_id, new_quantity)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, f"Новое количество: {new_quantity}")

@dp.callback_query(lambda c: c.data.startswith("decrease_"))
async def admin_decrease(callback: CallbackQuery):
    flavor_id = int(callback.data.split("_")[1])
    flavor = await get_flavor_by_id(flavor_id)
    new_quantity = max(0, flavor[3] - 1)
    await update_flavor_quantity(flavor_id, new_quantity)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, f"Новое количество: {new_quantity}")

@dp.callback_query(lambda c: c.data.startswith("manual_"))
async def admin_manual(callback: CallbackQuery, state: FSMContext):
    flavor_id = int(callback.data.split("_")[1])
    await state.set_state(AdminStates.EnterManualQuantity)
    await state.update_data(flavor_id=flavor_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Введите новое количество:")

@dp.callback_query(lambda c: c.data.startswith("edit_product_name_"))
async def admin_edit_product_name(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[3])
    await state.set_state(AdminStates.EnterNewProductNameEdit)
    await state.update_data(product_id=product_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Введите новое название товара:")

@dp.callback_query(lambda c: c.data.startswith("edit_flavor_price_"))
async def admin_edit_flavor_price(callback: CallbackQuery, state: FSMContext):
    flavor_id = int(callback.data.split("_")[3])
    await state.set_state(AdminStates.EnterNewFlavorPriceEdit)
    await state.update_data(flavor_id=flavor_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Введите новую цену для вкуса:")

@dp.callback_query(lambda c: c.data.startswith("admin_prev_"))
async def admin_prev(callback: CallbackQuery):
    location_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, location_id, offset)

@dp.callback_query(lambda c: c.data.startswith("admin_next_"))
async def admin_next(callback: CallbackQuery):
    location_id, offset = map(int, callback.data.split("_")[2:])
    await bot.answer_callback_query(callback.id)
    await show_admin_products(callback.message, location_id, offset)

@dp.callback_query(lambda c: c.data.startswith("admin_flavor_prev_"))
async def admin_flavor_prev(callback: CallbackQuery):
    location_id, product_id, offset = map(int, callback.data.split("_")[3:])
    await bot.answer_callback_query(callback.id)
    await show_admin_flavors(callback.message, location_id, product_id, offset)

@dp.callback_query(lambda c: c.data.startswith("admin_flavor_next_"))
async def admin_flavor_next(callback: CallbackQuery):
    location_id, product_id, offset = map(int, callback.data.split("_")[3:])
    await bot.answer_callback_query(callback.id)
    await show_admin_flavors(callback.message, location_id, product_id, offset)

@dp.callback_query(lambda c: c.data.startswith("add_product_"))
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    location_id = int(callback.data.split("_")[2])
    await state.set_state(AdminStates.EnterNewProductName)
    await state.update_data(location_id=location_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Введите название товара:")

@dp.callback_query(lambda c: c.data.startswith("add_flavor_"))
async def admin_add_flavor(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.set_state(AdminStates.EnterNewFlavorName)
    await state.update_data(product_id=product_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Введите название вкуса:")

@dp.callback_query(lambda c: c.data.startswith("delete_flavor_"))
async def admin_delete_flavor(callback: CallbackQuery):
    flavor_id = int(callback.data.split("_")[2])
    await delete_flavor_db(flavor_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Вкус успешно удален")

@dp.callback_query(lambda c: c.data.startswith("delete_product_"))
async def admin_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    await delete_product_db(product_id)
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, "Товар и все его вкусы удалены")

# FSM для админа
@dp.message(AdminStates.EnterManualQuantity)
async def process_manual_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    flavor_id = data['flavor_id']
    new_quantity = int(message.text)
    await update_flavor_quantity(flavor_id, new_quantity)
    await message.answer(f"Новое количество: {new_quantity}")
    await state.clear()

@dp.message(AdminStates.EnterNewProductName)
async def process_product_name(message: Message, state: FSMContext):
    data = await state.get_data()
    location_id = data['location_id']
    product_id = await add_product(location_id, message.text)
    await state.update_data(product_id=product_id)
    await state.set_state(AdminStates.EnterNewFlavorName)
    await message.answer("Введите название первого вкуса:")

@dp.message(AdminStates.EnterNewFlavorName)
async def process_flavor_name(message: Message, state: FSMContext):
    await state.update_data(flavor_name=message.text)
    await state.set_state(AdminStates.EnterNewFlavorQuantity)
    await message.answer("Введите количество:")

@dp.message(AdminStates.EnterNewFlavorQuantity)
async def process_flavor_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity < 0:
            raise ValueError
        await state.update_data(quantity=quantity)
        await state.set_state(AdminStates.EnterNewFlavorPrice)
        await message.answer("Введите цену:")
    except ValueError:
        await message.answer("Введите корректное число (например, 100)")

@dp.message(AdminStates.EnterNewFlavorPrice)
async def process_flavor_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
        data = await state.get_data()
        await add_flavor(data['product_id'], data['flavor_name'], data['quantity'], price)
        keyboard = [[InlineKeyboardButton(text="К выбору магазина", callback_data="locations")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await message.answer("✅ Вкус успешно добавлен!", reply_markup=reply_markup)
        await state.clear()
    except ValueError:
        await message.answer("Введите корректную цену (например, 500)")

@dp.message(AdminStates.EnterNewProductNameEdit)
async def process_product_name_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    new_name = message.text
    await update_product_name(product_id, new_name)
    keyboard = [[InlineKeyboardButton(text="К выбору магазина", callback_data="locations")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(f"Название товара обновлено: {new_name}", reply_markup=reply_markup)
    await state.clear()

@dp.message(AdminStates.EnterNewFlavorPriceEdit)
async def process_flavor_price_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    flavor_id = data['flavor_id']
    new_price = int(message.text)
    if new_price <= 0:
        await message.answer("Введите корректную цену (например, 500)")
        return
    await update_flavor_price(flavor_id, new_price)
    keyboard = [[InlineKeyboardButton(text="К выбору магазина", callback_data="locations")]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer(f"Цена вкуса обновлена: {new_price} руб.", reply_markup=reply_markup)
    await state.clear()

async def on_startup(dp):
    await init_db()

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot, on_startup=on_startup, skip_updates=True))