import aiosqlite

async def init_db():
    async with aiosqlite.connect("../shop.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Aromas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                aroma_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                category TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Products(id)
            )
        ''')
        await db.commit()

# Получение списка товаров с количеством ароматов и пагинацией (без сортировки в SQL)
async def get_products(offset=0, limit=10):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('''
            SELECT p.id, p.name, COUNT(a.id) as aroma_count
            FROM Products p
            LEFT JOIN Aromas a ON p.id = a.product_id
            GROUP BY p.id, p.name
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return await cursor.fetchall()

# Получение списка ароматов для товара с пагинацией (без сортировки в SQL)
async def get_aromas(product_id, offset=0, limit=10):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute(
            'SELECT id, aroma_name, quantity, category FROM Aromas WHERE product_id = ? LIMIT ? OFFSET ?',
            (product_id, limit, offset)
        )
        return await cursor.fetchall()

# Получение всех ароматов с количеством < 251 гр (без сортировки в SQL)
async def get_low_stock_aromas():
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('''
            SELECT p.name, a.aroma_name, a.quantity, a.category
            FROM Aromas a
            JOIN Products p ON a.product_id = p.id
            WHERE a.quantity < 251
        ''')
        return await cursor.fetchall()

# Получение ароматов по категории (A, B, C) (без сортировки в SQL)
async def get_aromas_by_category(category):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('''
            SELECT p.name, a.aroma_name, a.quantity, a.category
            FROM Aromas a
            JOIN Products p ON a.product_id = p.id
            WHERE a.category = ?
        ''', (category,))
        return await cursor.fetchall()

# Подсчёт общего количества грамм всех ароматов
async def get_total_quantity():
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('SELECT SUM(quantity) FROM Aromas')
        result = await cursor.fetchone()
        return result[0] if result[0] is not None else 0

# Получение информации о товаре по ID
async def get_product_by_id(product_id):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('SELECT id, name FROM Products WHERE id = ?', (product_id,))
        return await cursor.fetchone()

# Получение информации об аромате по ID
async def get_aroma_by_id(aroma_id):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute(
            'SELECT id, product_id, aroma_name, quantity, category FROM Aromas WHERE id = ?',
            (aroma_id,)
        )
        return await cursor.fetchone()

# Добавление нового товара
async def add_product(name):
    async with aiosqlite.connect('../shop.db') as db:
        cursor = await db.execute('INSERT INTO Products (name) VALUES (?)', (name,))
        await db.commit()
        return cursor.lastrowid

# Добавление нового аромата
async def add_aroma(product_id, aroma_name, quantity, category):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute(
            'INSERT INTO Aromas (product_id, aroma_name, quantity, category) VALUES (?, ?, ?, ?)',
            (product_id, aroma_name, quantity, category)
        )
        await db.commit()

# Обновление названия товара
async def update_product_name(product_id, new_name):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute('UPDATE Products SET name = ? WHERE id = ?', (new_name, product_id))
        await db.commit()

# Обновление количества аромата
async def update_aroma_quantity(aroma_id, new_quantity):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute('UPDATE Aromas SET quantity = ? WHERE id = ?', (new_quantity, aroma_id))
        await db.commit()

# Обновление категории аромата
async def update_aroma_category(aroma_id, new_category):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute('UPDATE Aromas SET category = ? WHERE id = ?', (new_category, aroma_id))
        await db.commit()

# Удаление товара (и всех его ароматов)
async def delete_product_db(product_id):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute('DELETE FROM Aromas WHERE product_id = ?', (product_id,))
        await db.execute('DELETE FROM Products WHERE id = ?', (product_id,))
        await db.commit()

# Удаление аромата
async def delete_aroma_db(aroma_id):
    async with aiosqlite.connect('../shop.db') as db:
        await db.execute('DELETE FROM Aromas WHERE id = ?', (aroma_id,))
        await db.commit()