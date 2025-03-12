import aiosqlite

async def init_db():
    async with aiosqlite.connect("shop.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Flavors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                flavor_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products(id)
            )
        ''')
        await db.commit()

# Получение списка товаров с количеством вкусов и пагинацией
async def get_products(offset=0, limit=10):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('''
            SELECT p.id, p.name, COUNT(f.id) as flavor_count
            FROM Products p
            LEFT JOIN Flavors f ON p.id = f.product_id
            GROUP BY p.id, p.name
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return await cursor.fetchall()

# Получение списка вкусов для товара с пагинацией
async def get_flavors(product_id, offset=0, limit=10):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute(
            'SELECT id, flavor_name, quantity, price FROM Flavors WHERE product_id = ? LIMIT ? OFFSET ?',
            (product_id, limit, offset)
        )
        return await cursor.fetchall()

# Получение информации о товаре по ID
async def get_product_by_id(product_id):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('SELECT id, name FROM Products WHERE id = ?', (product_id,))
        return await cursor.fetchone()

# Получение информации о вкусе по ID
async def get_flavor_by_id(flavor_id):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute(
            'SELECT id, product_id, flavor_name, quantity, price FROM Flavors WHERE id = ?',
            (flavor_id,)
        )
        return await cursor.fetchone()

# Добавление нового товара
async def add_product(name):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('INSERT INTO Products (name) VALUES (?)', (name,))
        await db.commit()
        return cursor.lastrowid

# Добавление нового вкуса
async def add_flavor(product_id, flavor_name, quantity, price):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute(
            'INSERT INTO Flavors (product_id, flavor_name, quantity, price) VALUES (?, ?, ?, ?)',
            (product_id, flavor_name, quantity, price)
        )
        await db.commit()

# Обновление названия товара
async def update_product_name(product_id, new_name):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('UPDATE Products SET name = ? WHERE id = ?', (new_name, product_id))
        await db.commit()

# Обновление количества вкуса
async def update_flavor_quantity(flavor_id, new_quantity):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('UPDATE Flavors SET quantity = ? WHERE id = ?', (new_quantity, flavor_id))
        await db.commit()

# Обновление цены вкуса
async def update_flavor_price(flavor_id, new_price):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('UPDATE Flavors SET price = ? WHERE id = ?', (new_price, flavor_id))
        await db.commit()

# Удаление товара (и всех его вкусов)
async def delete_product_db(product_id):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('DELETE FROM Flavors WHERE product_id = ?', (product_id,))
        await db.execute('DELETE FROM Products WHERE id = ?', (product_id,))
        await db.commit()

# Удаление вкуса
async def delete_flavor_db(flavor_id):
    async with aiosqlite.connect('shop.db') as db:
        await db.execute('DELETE FROM Flavors WHERE id = ?', (flavor_id,))
        await db.commit()