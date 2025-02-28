import aiosqlite

async def init_db():
    async with aiosqlite.connect("shop.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (location_id) REFERENCES Locations(id)
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
        await db.execute('INSERT OR IGNORE INTO Locations (id, name) VALUES (1, "Магазин 1")')
        await db.execute('INSERT OR IGNORE INTO Locations (id, name) VALUES (2, "Магазин 2")')
        await db.execute('INSERT OR IGNORE INTO Locations (id, name) VALUES (3, "Магазин 3")')
        await db.commit()

# Получение списка магазинов с количеством товаров
async def get_locations():
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('''
            SELECT l.id, l.name, COUNT(p.id) as product_count
            FROM Locations l
            LEFT JOIN Products p ON l.id = p.location_id
            GROUP BY l.id, l.name
        ''')
        return await cursor.fetchall()

# Получение списка товаров по локации с количеством вкусов
async def get_products(location_id, offset=0, limit=10):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('''
            SELECT p.id, p.name, COUNT(f.id) as flavor_count
            FROM Products p
            LEFT JOIN Flavors f ON p.id = f.product_id
            WHERE p.location_id = ?
            GROUP BY p.id, p.name
            LIMIT ? OFFSET ?
        ''', (location_id, limit, offset))
        return await cursor.fetchall()

# Получение списка вкусов для товара
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
        cursor = await db.execute('SELECT id, location_id, name FROM Products WHERE id = ?', (product_id,))
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
async def add_product(location_id, name):
    async with aiosqlite.connect('shop.db') as db:
        cursor = await db.execute('INSERT INTO Products (location_id, name) VALUES (?, ?)', (location_id, name))
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
