import pandas as pd
import database as db
from datetime import datetime
import os

async def generate_excel_report(period='daily'):
    orders = await db.get_detailed_orders(period)
    
    if not orders:
        return None
    
    from config import PRODUCTS_PRICING
    import json
    
    report_data = []
    for o in orders:
        cart = json.loads(o['cart_json'])
        readable_cart = []
        for p_id, qty in cart.items():
            p_name = PRODUCTS_PRICING.get(p_id, {}).get('name', p_id)
            readable_cart.append(f"{p_name}: {qty} dona")
        
        cart_str = ", ".join(readable_cart)

        report_data.append({
            "ID": f"#{o['id']}",
            "Mijoz": o['name'],
            "Tel": o['phone'],
            "Do'kon": o.get('store', 'Noma\'lum'),
            "Buyurtma": cart_str,
            "Savdo (so'm)": o['total_revenue'],
            "Tannarx (so'm)": o['total_cost'],
            "Foyda (so'm)": o['profit'],
            "Sana": o['created_at']
        })
        
    df = pd.DataFrame(report_data)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"report_{period}_{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    
    return filename
