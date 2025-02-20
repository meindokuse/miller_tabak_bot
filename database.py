import aiosqlite


async def init_db():
    async with aiosqlite.connect("shop.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price INTEGER NOT NULL
            )
        ''')
        await db.commit()

# Получение списка товаров с пагинацией
async def get_products(offset=0, limit=20):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('SELECT * FROM products LIMIT ? OFFSET ?', (limit, offset))
        return await cursor.fetchall()

# Получение информации о товаре по ID
async def get_product_by_id(product_id):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        return await cursor.fetchone()

# Добавление нового товара
async def add_product(name, quantity, price):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)', (name, quantity, price))
        await db.commit()

# Обновление количества товара
async def update_product_quantity(product_id, new_quantity):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product_id))
        await db.commit()

# Удаление товара
async def delete_product_db(product_id):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('DELETE FROM products WHERE id = ?', (product_id,))
        await db.commit()

