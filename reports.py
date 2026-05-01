import pandas as pd
import database as db
from datetime import datetime
import uuid

async def generate_excel_report(period='daily'):
    orders = await db.get_detailed_orders(period)
    
    if not orders:
        return None
    
    from config import PRODUCTS_PRICING
    import json
    
    import openpyxl.styles
    report_data = []
    for o in orders:
        cart = json.loads(o['cart_json'])
        mahsulotlar_list = []
        soni_list = []
        for p_id, qty in cart.items():
            p_name = PRODUCTS_PRICING.get(p_id, {}).get('name', p_id)
            mahsulotlar_list.append(p_name)
            soni_list.append(str(qty))
        
        mahsulot_str = "\n".join(mahsulotlar_list)
        soni_str = "\n".join(soni_list)
        
        try:
            sana_val = datetime.strptime(o['created_at'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
        except (ValueError, TypeError):
            sana_val = str(o['created_at'])[:10]

        report_data.append({
            "Sana": sana_val,
            "Ism/Username": o['name'],
            "Joy": "", 
            "Rasta/Do'kon raqami": o.get('store', "Noma'lum"),
            "Mahsulot": mahsulot_str,
            "Soni": soni_str,
            "Jami summa": o['total_revenue'],
            "Foyda": o['profit'],
            "Kassa": o['total_cost']
        })
        
    df = pd.DataFrame(report_data)
    
    if not df.empty:
        total_summa = df["Jami summa"].sum()
        total_foyda = df["Foyda"].sum()
        total_kassa = df["Kassa"].sum()
        
        df = pd.concat([df, pd.DataFrame([{col: "" for col in df.columns}])], ignore_index=True)
        
        labels_row = {col: "" for col in df.columns}
        labels_row["Jami summa"] = "Jami summa"
        labels_row["Foyda"] = "Jami foyda"
        labels_row["Kassa"] = "Jami kassa"
        df = pd.concat([df, pd.DataFrame([labels_row])], ignore_index=True)
        
        totals_row = {col: "" for col in df.columns}
        totals_row["Jami summa"] = total_summa
        totals_row["Foyda"] = total_foyda
        totals_row["Kassa"] = total_kassa
        df = pd.concat([df, pd.DataFrame([totals_row])], ignore_index=True)
    
    # Save file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{period}_{timestamp}_{uuid.uuid4().hex[:8]}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hisobot')
        worksheet = writer.sheets['Hisobot']
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(wrapText=True, vertical='top')
    
    return filename
