import aiosqlite
import json
from datetime import datetime
import os

DB_PATH = os.getenv("DB_PATH", "orders.db")
_db = None

async def get_db():
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
    return _db

async def close_db():
    global _db
    if _db is not None:
        await _db.close()
        _db = None

def _summary_query(period: str):
    import pytz
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    now_tashkent = datetime.now(tashkent_tz)

    if period == 'daily':
        date_filter = now_tashkent.strftime('%Y-%m-%d')
        return (
            "SELECT * FROM orders WHERE status = 'accepted' AND date(created_at) = ?",
            (date_filter,),
        )
    if period == 'monthly':
        date_filter = now_tashkent.strftime('%Y-%m')
        return (
            "SELECT * FROM orders WHERE status = 'accepted' AND strftime('%Y-%m', created_at) = ?",
            (date_filter,),
        )
    raise ValueError("Invalid period. Use 'daily' or 'monthly'.")


async def init_db():
    db = await get_db()
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
    
    # Self-migration: Check if columns exist (for existing databases)
    cursor = await db.execute("PRAGMA table_info(orders)")
    columns = [row[1] for row in await cursor.fetchall()]
    
    if "location_lat" not in columns:
        await db.execute("ALTER TABLE orders ADD COLUMN location_lat REAL")
    if "location_lon" not in columns:
        await db.execute("ALTER TABLE orders ADD COLUMN location_lon REAL")

    # Inventory table with prices
    await db.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            in_stock INTEGER DEFAULT 1,
            cost REAL DEFAULT 0,
            sell REAL DEFAULT 0
        )
    ''')
    
    # Self-migration: check if cost and sell exist in inventory
    cursor = await db.execute("PRAGMA table_info(inventory)")
    inv_columns = [row[1] for row in await cursor.fetchall()]
    if "cost" not in inv_columns:
        await db.execute("ALTER TABLE inventory ADD COLUMN cost REAL DEFAULT 0")
    if "sell" not in inv_columns:
        await db.execute("ALTER TABLE inventory ADD COLUMN sell REAL DEFAULT 0")

    # Initial inventory setup from config
    from config import PRODUCTS_PRICING
    for p_id, p_info in PRODUCTS_PRICING.items():
        await db.execute('''
            INSERT INTO inventory (product_id, product_name, in_stock, cost, sell) 
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(product_id) DO UPDATE SET
                product_name = excluded.product_name,
                cost = CASE WHEN cost = 0 THEN excluded.cost ELSE cost END,
                sell = CASE WHEN sell = 0 THEN excluded.sell ELSE sell END
        ''', (p_id, p_info["name"], p_info["cost"], p_info["sell"]))
        
    await db.commit()

async def add_order(telegram_id: int, name: str, phone: str, store: str, lat: float, lon: float, cart: dict, total_cost: float, total_revenue: float, profit: float):
    import pytz
    from datetime import datetime
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    now_tashkent = datetime.now(tashkent_tz).strftime('%Y-%m-%d %H:%M:%S')

    db = await get_db()
    cursor = await db.execute('''
        INSERT INTO orders (telegram_id, name, phone, store, location_lat, location_lon, cart_json, total_cost, total_revenue, profit, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (telegram_id, name, phone, store, lat, lon, json.dumps(cart), total_cost, total_revenue, profit, now_tashkent))
    await db.commit()
    return cursor.lastrowid


async def update_order_status(order_id: int, status: str):
    db = await get_db()
    await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    await db.commit()


async def get_order_by_id(order_id: int):
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None

async def get_inventory():
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute("SELECT * FROM inventory")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

async def toggle_stock(product_id: str):
    db = await get_db()
    await db.execute('UPDATE inventory SET in_stock = 1 - in_stock WHERE product_id = ?', (product_id,))
    await db.commit()

async def get_summary(period='daily'):
    """period: 'daily' or 'monthly'"""
    sql, params = _summary_query(period)
        
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(sql, params)
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
    sql, params = _summary_query(period)
        
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(sql, params)
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

async def get_products_pricing():
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute("SELECT product_id, product_name, cost, sell FROM inventory")
    rows = await cursor.fetchall()
    pricing = {}
    for row in rows:
        pricing[row["product_id"]] = {
            "name": row["product_name"],
            "cost": row["cost"],
            "sell": row["sell"]
        }
    return pricing

async def get_latest_pending_order_by_user(telegram_id: int):
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(
        "SELECT * FROM orders WHERE telegram_id = ? AND status = 'pending' ORDER BY id DESC LIMIT 1",
        (telegram_id,)
    )
    row = await cursor.fetchone()
    return dict(row) if row else None

async def update_order_location(order_id: int, lat: float, lon: float):
    db = await get_db()
    await db.execute(
        "UPDATE orders SET location_lat = ?, location_lon = ? WHERE id = ?",
        (lat, lon, order_id)
    )
    await db.commit()

async def update_product_price(product_id: str, cost: float, sell: float):
    db = await get_db()
    await db.execute(
        "UPDATE inventory SET cost = ?, sell = ? WHERE product_id = ?",
        (cost, sell, product_id)
    )
    await db.commit()

async def get_orders_by_user(telegram_id: int):
    db = await get_db()
    db.row_factory = aiosqlite.Row
    cursor = await db.execute(
        "SELECT * FROM orders WHERE telegram_id = ? ORDER BY id DESC LIMIT 10",
        (telegram_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]

async def get_admin_stats():
    import pytz
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    now = datetime.now(tashkent_tz)
    
    today_str = now.strftime('%Y-%m-%d')
    from datetime import timedelta
    yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    month_str = now.strftime('%Y-%m')
    
    db = await get_db()
    db.row_factory = aiosqlite.Row
    
    # Today's stats
    cursor = await db.execute(
        "SELECT COUNT(*), SUM(total_revenue), SUM(profit) FROM orders WHERE status = 'accepted' AND date(created_at) = ?",
        (today_str,)
    )
    today_row = await cursor.fetchone()
    today_count = today_row[0] or 0
    today_rev = today_row[1] or 0
    today_profit = today_row[2] or 0
    
    # Yesterday's stats
    cursor = await db.execute(
        "SELECT COUNT(*), SUM(total_revenue), SUM(profit) FROM orders WHERE status = 'accepted' AND date(created_at) = ?",
        (yesterday_str,)
    )
    yesterday_row = await cursor.fetchone()
    yesterday_count = yesterday_row[0] or 0
    yesterday_rev = yesterday_row[1] or 0
    yesterday_profit = yesterday_row[2] or 0
    
    # This month's stats
    cursor = await db.execute(
        "SELECT COUNT(*), SUM(total_revenue), SUM(profit) FROM orders WHERE status = 'accepted' AND strftime('%Y-%m', created_at) = ?",
        (month_str,)
    )
    month_row = await cursor.fetchone()
    month_count = month_row[0] or 0
    month_rev = month_row[1] or 0
    month_profit = month_row[2] or 0
    
    # Top products today
    cursor = await db.execute(
        "SELECT cart_json FROM orders WHERE status = 'accepted' AND date(created_at) = ?",
        (today_str,)
    )
    rows = await cursor.fetchall()
    product_sales = {}
    for row in rows:
        try:
            cart = json.loads(row['cart_json'])
            for p_id, qty in cart.items():
                product_sales[p_id] = product_sales.get(p_id, 0) + int(qty)
        except Exception:
            continue
            
    # Sort top products
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        "today": {"count": today_count, "rev": today_rev, "profit": today_profit},
        "yesterday": {"count": yesterday_count, "rev": yesterday_rev, "profit": yesterday_profit},
        "month": {"count": month_count, "rev": month_rev, "profit": month_profit},
        "top_products": top_products
    }

