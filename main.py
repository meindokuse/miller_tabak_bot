import asyncio

from aiogram import Dispatcher, Bot, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from database import get_product_by_id, update_product_quantity, init_db, add_product, delete_product_db
from service import show_admin_products, show_user_products

API_TOKEN = '8037910201:AAHEwbfNG4feas1J4N71inZAO0l-B8WZS6o'
ADMIN_CHAT_ID = 1082039395

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


class AdminStates(StatesGroup):
    EnterNewProductName = State()
    EnterNewProductQuantity = State()
    EnterNewProductPrice = State()
    EnterManualQuantity = State()


@dp.callback_query(F.data == 'main')
@dp.message(CommandStart())
async def cmd_start(event):
    await init_db()
    if isinstance(event, Message):
        chat_id = event.chat.id
        if chat_id == ADMIN_CHAT_ID:
            await show_admin_products(event)
        else:
            await show_user_products(event)
    elif isinstance(event, CallbackQuery):
        chat_id = event.message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            await show_admin_products(event.message)
        else:
            await show_user_products(event.message)


@dp.callback_query(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data

    if data.startswith("product_"):
        product_id = int(data.split("_")[1])
        product = await get_product_by_id(product_id)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id,
                               f"Название: {product[1]}\nКоличество: {product[2]}\nЦена: {product[3]}")

    elif data.startswith("admin_product_"):
        product_id = int(data.split("_")[2])
        product = await get_product_by_id(product_id)
        keyboard = [
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{product_id}")],
            [InlineKeyboardButton(text="✏️ Изменить количество", callback_data=f"change_quantity_{product_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id,
                               f"Название: {product[1]}\nКоличество: {product[2]}\nЦена: {product[3]} Руб.",
                               reply_markup=reply_markup)

    elif data.startswith("change_quantity_"):
        product_id = int(data.split("_")[2])
        product = await get_product_by_id(product_id)
        keyboard = [
            [InlineKeyboardButton(text="➕ +1", callback_data=f"increase_{product_id}")],
            [InlineKeyboardButton(text="➖ -1", callback_data=f"decrease_{product_id}")],
            [InlineKeyboardButton(text="📝 Ввести вручную", callback_data=f"manual_{product_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, f"Текущее количество: {product[2]}",
                               reply_markup=reply_markup)

    elif data.startswith("increase_"):
        keyboard = [
            [InlineKeyboardButton(text="В начало", callback_data=f"main")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        product_id = int(data.split("_")[1])
        product = await get_product_by_id(product_id)
        new_quantity = product[2] + 1
        await update_product_quantity(product_id, new_quantity)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, f"Новое количество: {new_quantity}",reply_markup=reply_markup)

    elif data.startswith("decrease_"):
        keyboard = [
            [InlineKeyboardButton(text="В начало", callback_data=f"main")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        product_id = int(data.split("_")[1])
        product = await get_product_by_id(product_id)
        new_quantity = product[2] - 1
        await update_product_quantity(product_id, new_quantity)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, f"Новое количество: {new_quantity}",reply_markup=reply_markup)

    elif data.startswith("manual_"):
        product_id = int(data.split("_")[1])
        await state.set_state(AdminStates.EnterManualQuantity)
        await state.update_data(product_id=product_id)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите новое количество:")

    elif data == "add_new_product":

        await state.set_state(AdminStates.EnterNewProductName)
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Введите название товара:")

    elif data.startswith("delete_"):
        try:
            product_id = int(data.split("_")[1])
            await delete_product_db(product_id)
            await bot.send_message(callback_query.from_user.id, "Продукт успешно удален")
        except Exception as e:
            await bot.send_message(callback_query.from_user.id, "Произошла ошибка при удалении продукта")


# @dp.callback_query(F.data.startswith("delete_"))
# async def delete_product(call: CallbackQuery):
#     try:
#         data = call.data
#         product_id = int(data.split("_")[2])
#         await delete_product_db(product_id)
#         await bot.answer_callback_query("Продукт успешно удален")
#     except Exception as e:
#         await bot.answer_callback_query("Произошла ошибка")


# Обработчик текстовых сообщений (для ввода количества вручную)
@dp.message(AdminStates.EnterManualQuantity)
async def process_manual_quantity(message: types.Message, state: FSMContext):
    keyboard = [
        [InlineKeyboardButton(text="В начало", callback_data=f"main")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    data = await state.get_data()
    product_id = data['product_id']
    new_quantity = int(message.text)
    await update_product_quantity(product_id, new_quantity)
    await message.answer(text = f"Новое количество: {new_quantity}",reply_markup=reply_markup)
    await state.clear()


@dp.message(AdminStates.EnterNewProductName)
async def process_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.EnterNewProductQuantity)
    await message.answer("Введите количество товара:")


# Обработчик ввода количества товара
@dp.message(AdminStates.EnterNewProductQuantity)
async def process_product_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity < 0:
            raise ValueError
        await state.update_data(quantity=quantity)
        await state.set_state(AdminStates.EnterNewProductPrice)
        await message.answer("Введите цену товара:")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число (например: 100)")


# Обработчик ввода цены товара
@dp.message(AdminStates.EnterNewProductPrice)
async def process_product_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError

        data = await state.get_data()
        await add_product(
            name=data['name'],
            quantity=data['quantity'],
            price=price
        )
        keyboard = [
            [InlineKeyboardButton(text="В начало", callback_data=f"main")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(text="✅ Товар успешно добавлен!", reply_markup=reply_markup)
        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректную цену (например: 500)")


async def on_startup(dp):
    await init_db()


if __name__ == '__main__':
    # Используем asyncio.run для запуска асинхронного кода
    asyncio.run(dp.start_polling(bot, on_startup=on_startup, skip_updates=True))
