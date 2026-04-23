from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import WEBAPP_URL
import urllib.parse

def get_main_menu(out_param=""):
    url = WEBAPP_URL
    if out_param:
        encoded_param = urllib.parse.quote(out_param)
        if "?" in url:
            url += f"&out_of_stock={encoded_param}"
        else:
            url += f"?out_of_stock={encoded_param}"
            
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish", web_app=WebAppInfo(url=url))],
            [KeyboardButton(text="📊 Hisobotni olish"), KeyboardButton(text="📦 Ombor boshqaruvi")]
        ],
        resize_keyboard=True
    )

def get_user_menu(out_param=""):
    url = WEBAPP_URL
    if out_param:
        encoded_param = urllib.parse.quote(out_param)
        if "?" in url:
            url += f"&out_of_stock={encoded_param}"
        else:
            url += f"?out_of_stock={encoded_param}"
            
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish", web_app=WebAppInfo(url=url))]
        ],
        resize_keyboard=True
    )

def get_admin_order_kb(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"order_accept_{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"order_reject_{order_id}")
            ]
        ]
    )

def get_report_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Kunlik hisobot", callback_data="report_daily"),
                InlineKeyboardButton(text="📅 Oylik hisobot", callback_data="report_monthly")
            ]
        ]
    )

def get_inventory_kb(inventory_list):
    kb = []
    for item in inventory_list:
        status = "✅" if item['in_stock'] else "❌"
        kb.append([InlineKeyboardButton(text=f"{item['product_name']} {status}", callback_data=f"toggle_{item['product_id']}")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_share_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Botni ulashish", url="https://t.me/share/url?url=https://t.me/SaxovataBaraka_buyurtma_bot&text=Shirinliklar va pechini buyurtma berish uchun bot!")]
        ]
    )
