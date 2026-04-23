# config.py

import os
from dotenv import load_dotenv
load_dotenv()

# Bot API tokeningizni BotFather(https://t.me/BotFather) orqali olasiz va shu yerga kiritasiz
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# O'zingizning Telegram ID raqamingiz. Bot orqali IDingizni @getmyid_bot dan bilib olishingiz mumkin.
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

# Guruh ID si. Barcha yangi buyurtmalar qabul qilinadigan telegram guruhining ID raqami. 
GROUP_ID = os.getenv("GROUP_ID", ADMIN_ID)

# Karta orqali to'lov uchun ulanish (O'z karta raqamingizni kiriting)
# Masalan 8600123456789012 ni o'z kartangizga o'zgartiring
CLICK_P2P_LINK = os.getenv("CLICK_P2P_LINK", "")
PAYME_CARD = os.getenv("PAYME_CARD", "")

# Miniapp Ssilkasi (Netlify yoki Vercel). Hozircha namuna uchun qilingan.
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

# Pishiriqlar narxlari va foyda hisoblash uchun ma'lumotlar
PRODUCTS_PRICING = {
    "Pechini 1": {"name": "Taplyonniy", "cost": 37500, "sell": 45000},
    "Pechini 2": {"name": "Yubileyniy", "cost": 36000, "sell": 45000},
    "Pechini 3": {"name": "Yulduz", "cost": 43500, "sell": 48000},
    "Pechini 4": {"name": "Olmali", "cost": 50000, "sell": 60000},
    "Pechini 5": {"name": "Pop Corn", "cost": 50000, "sell": 60000},
    "Pechini 6": {"name": "Azbuka", "cost": 57500, "sell": 70000}
}
