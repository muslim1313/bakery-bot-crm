import aiosqlite
import json
from datetime import datetime
import os

DB_PATH = os.getenv("DB_PATH", "orders.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Orders table with both Store and Location
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                phone TEXT,
                store TEXT,
                location_lat REAL,
                location_lon REAL,
                cart_json TEXT,
                total_cost REAL,
                total_revenue REAL,
                profit REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Self-migration: Check if columns exist (for existing databases on Railway/Server)
        cursor = await db.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in await cursor.fetchall()]
        
        if "location_lat" not in columns:
            await db.execute("ALTER TABLE orders ADD COLUMN location_lat REAL")
        if "location_lon" not in columns:
            await db.execute("ALTER TABLE orders ADD COLUMN location_lon REAL")

        # Inventory table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                product_id TEXT PRIMARY KEY,
                product_name TEXT,
                in_stock INTEGER DEFAULT 1
            )
        ''')
        
        # Initial inventory setup from config
        from config import PRODUCTS_PRICING
        for p_id, p_info in PRODUCTS_PRICING.items():
            await db.execute('''
                INSERT OR IGNORE INTO inventory (product_id, product_name, in_stock) 
                VALUES (?, ?, 1)
            ''', (p_id, p_info["name"]))
            
        await db.commit()

async def add_order(telegram_id: int, name: str, phone: str, store: str, lat: float, lon: float, cart: dict, total_cost: float, total_revenue: float, profit: float):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO orders (telegram_id, name, phone, store, location_lat, location_lon, cart_json, total_cost, total_revenue, profit, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (telegram_id, name, phone, store, lat, lon, json.dumps(cart), total_cost, total_revenue, profit))
        await db.commit()
        return cursor.lastrowid

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def get_inventory():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM inventory")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def toggle_stock(product_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE inventory SET in_stock = 1 - in_stock WHERE product_id = ?', (product_id,))
        await db.commit()

async def get_summary(period='daily'):
    """period: 'daily' or 'monthly'"""
    if period == 'daily':
        date_filter = datetime.now().strftime('%Y-%m-%d')
        sql = f"SELECT * FROM orders WHERE status = 'accepted' AND date(created_at, 'localtime') = '{date_filter}'"
    else:
        date_filter = datetime.now().strftime('%Y-%m')
        sql = f"SELECT * FROM orders WHERE status = 'accepted' AND strftime('%Y-%m', created_at, 'localtime') = '{date_filter}'"
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()
        
    summary = {
        "count": len(rows),
        "total_cost": sum(row['total_cost'] for row in rows),
        "total_revenue": sum(row['total_revenue'] for row in rows),
        "total_profit": sum(row['profit'] for row in rows),
        "items": {}
    }
    
    for row in rows:
        cart = json.loads(row['cart_json'])
        for p_id, qty in cart.items():
            summary["items"][p_id] = summary["items"].get(p_id, 0) + qty
            
    return summary

async def get_detailed_orders(period='daily'):
    if period == 'daily':
        date_filter = datetime.now().strftime('%Y-%m-%d')
        sql = f"SELECT * FROM orders WHERE status = 'accepted' AND date(created_at, 'localtime') = '{date_filter}'"
    else:
        date_filter = datetime.now().strftime('%Y-%m')
        sql = f"SELECT * FROM orders WHERE status = 'accepted' AND strftime('%Y-%m', created_at, 'localtime') = '{date_filter}'"
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
