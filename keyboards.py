from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import WEBAPP_URL
import urllib.parse


def build_webapp_url(out_param="", prices_param=""):
    """WEBAPP_URL da allaqachon ? bo'lsa, qo'shimcha parametrlar & bilan ulanadi."""
    url = WEBAPP_URL.rstrip("/")
    params = []
    if out_param:
        params.append(f"out_of_stock={urllib.parse.quote(out_param)}")
    if prices_param:
        params.append(f"prices={prices_param}")
    if params:
        url += ("&" if "?" in url else "?") + "&".join(params)
    return url


def get_main_menu(out_param="", prices_param=""):
    url = build_webapp_url(out_param, prices_param)
            
    print(f"DEBUG: WebApp URL is '{url}'")
            
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish", web_app=WebAppInfo(url=url))],
            [KeyboardButton(text="📊 Hisobotni olish"), KeyboardButton(text="📦 Ombor boshqaruvi")],
            [KeyboardButton(text="📈 Tezkor Statistika"), KeyboardButton(text="📋 Buyurtmalarim")]
        ],
        resize_keyboard=True
    )

def get_user_menu(out_param="", prices_param=""):
    url = build_webapp_url(out_param, prices_param)
            
    print(f"DEBUG: WebApp User URL is '{url}'")
            
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish", web_app=WebAppInfo(url=url))],
            [KeyboardButton(text="📋 Buyurtmalarim")]
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
    share_text = urllib.parse.quote("Shirinliklar va pechini buyurtma berish uchun bot!")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Botni ulashish", 
                url=f"https://t.me/share/url?url=https://t.me/SaxovataBaraka_buyurtma_bot&text={share_text}"
            )]
        ]
    )
