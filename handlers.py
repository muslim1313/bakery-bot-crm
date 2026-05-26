from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions, InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import ADMIN_ID, GROUP_ID, CONTACT_PHONE, CONTACT_USERNAME
import database as db
import keyboards as kb
import json
import html
import logging
import re

logger = logging.getLogger(__name__)
MAX_QTY_PER_ITEM = 1000


def _is_admin(user_id: int) -> bool:
    return str(user_id) == str(ADMIN_ID)


def _normalize_text(value, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    cleaned = value.strip()
    return cleaned if cleaned else fallback


def _parse_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


async def _webapp_menu_params():
    inventory = await db.get_inventory()
    out_of_stock_ids = [item["product_id"] for item in inventory if not item["in_stock"]]
    out_param = ",".join(out_of_stock_ids)
    prices = {item["product_id"]: item["sell"] for item in inventory}
    import urllib.parse
    prices_param = urllib.parse.quote(json.dumps(prices, ensure_ascii=False))
    return out_param, prices_param


def _contact_links():
    username_clean = CONTACT_USERNAME.strip()
    if username_clean.startswith("@"):
        username_clean = username_clean[1:]

    tg_url = f"https://t.me/{username_clean}" if username_clean else None
    return tg_url

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Get inventory to handle out-of-stock and prices
    try:
        out_param, prices_param = await _webapp_menu_params()
    except Exception as e:
        print(f"DB Error in start: {e}")
        out_param = ""
        prices_param = ""

    welcome_text = (
        "<b>Saxovat Baraka</b> buyurtma tizimiga xush kelibsiz!\n\n"
        "Buyurtma berish uchun quyidagi tugmani bosing."
    )
    
    # Check admin status
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    
    if is_admin:
        reply_markup = kb.get_main_menu(out_param, prices_param)
    else:
        reply_markup = kb.get_user_menu(out_param, prices_param)

    from aiogram.types import LinkPreviewOptions
    # Combine into one message for better keyboard reliability
    await message.answer(
        welcome_text, 
        reply_markup=reply_markup, 
        parse_mode="HTML", 
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )

@router.message(F.web_app_data)
async def web_app_data_handler(message: Message, bot: Bot):
    try:
        data = json.loads(message.web_app_data.data)
        cart = data.get("cart", {})
        if not isinstance(cart, dict) or not cart:
            await message.answer("Savatcha bo'sh yoki ma'lumotlar noto'g'ri kiritildi.")
            return

        phone_raw = data.get("phone", "").strip()
        # Uzbekistan phone regex format check
        phone_match = re.match(r"^\+?(998)?\d{9}$", phone_raw)
        if not phone_match:
            await message.answer("Kiritilgan telefon raqami noto'g'ri. Iltimos, +998XXXXXXXXX formatida kiriting.")
            return
            
        phone = phone_raw if phone_raw.startswith("+") else f"+{phone_raw}"
        client_name = _normalize_text(data.get("name"), message.from_user.full_name or "Mijoz")
        store_name = _normalize_text(data.get("store"), "Do'kon")
        
        if len(client_name) > 100 or len(store_name) > 150:
            await message.answer("Ism yoki do'kon nomi juda uzun kiritilgan. Iltimos, qisqaroq qilib qayta kiriting.")
            return

        lat = _parse_float(data.get("lat"))
        lon = _parse_float(data.get("lon"))
        if lat == 0.0 and lon == 0.0:
            lat = None
            lon = None

        total_cost = 0
        total_revenue = 0
        order_details = ""
        clean_cart = {}

        products_pricing = await db.get_products_pricing()
        inventory = await db.get_inventory()
        stock_map = {item["product_id"]: bool(item["in_stock"]) for item in inventory}

        for p_id, qty in cart.items():
            product = products_pricing.get(p_id)
            if not product:
                continue

            try:
                qty_int = int(qty)
            except (TypeError, ValueError):
                continue

            if qty_int < 1 or qty_int > MAX_QTY_PER_ITEM:
                continue

            if not stock_map.get(p_id, True):
                await message.answer(f"{product['name']} hozirda omborda mavjud emas. Iltimos, savatchani yangilang.")
                return

            clean_cart[p_id] = qty_int
            cost = product["cost"] * qty_int
            sell = product["sell"] * qty_int
            total_cost += cost
            total_revenue += sell
            order_details += f"  {product['name']}: {qty_int} dona\n"

        if not clean_cart:
            await message.answer("Savatchada buyurtma uchun yaroqli mahsulot topilmadi.")
            return

        profit = total_revenue - total_cost

        # Save to DB
        order_id = await db.add_order(
            message.from_user.id, client_name, phone, store_name, lat, lon, clean_cart,
            total_cost, total_revenue, profit
        )

        # Send info to User
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        if lat is None or lon is None:
            location_kb = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📍 Joylashuvni tasdiqlash", request_location=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer(
                f"<b>Buyurtmangiz #{order_id} qabul qilindi.</b>\n\n"
                f"Jami summa: {total_revenue:,} so'm\n\n"
                f"Iltimos, buyurtmangizni tezroq yetkazib berishimiz uchun quyidagi <b>'📍 Joylashuvni tasdiqlash'</b> tugmasini bosing.",
                reply_markup=location_kb,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"<b>Buyurtmangiz muvaffaqiyatli qabul qilindi.</b>\n\n"
                f"Buyurtma ID: #{order_id}\n"
                f"Jami summa: {total_revenue:,} so'm\n\n"
                f"Holati: <b>Kutish jarayonida</b>",
                parse_mode="HTML"
            )

        # Send Order Card to Group/Admin
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        admin_card = (
            f"<b>YANGI BUYURTMA #{order_id}</b>\n\n"
            f"Mijoz: {html.escape(client_name)}\n"
            f"Telefon: <code>{html.escape(phone)}</code>\n"
            f"Do'kon: {html.escape(store_name)}\n"
        )
        
        if lat is not None and lon is not None:
            admin_card += f"Manzil: <a href='{maps_link}'>Xaritada ko'rish</a>\n\n"
        else:
            admin_card += "Manzil: Yuborilmagan (Tasdiqlash kutilmoqda)\n\n"

        admin_card += (
            f"Mahsulotlar:\n{order_details}\n"
            f"Jami summa: {total_revenue:,} so'm\n"
            f"Sof foyda: {profit:,} so'm"
        )

        await bot.send_message(
            GROUP_ID, 
            admin_card, 
            parse_mode="HTML", 
            reply_markup=kb.get_admin_order_kb(order_id),
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )

    except Exception:
        logger.exception("web_app_data_handler failed")
        await message.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")

@router.message(F.location)
async def location_handler(message: Message, bot: Bot):
    try:
        order = await db.get_latest_pending_order_by_user(message.from_user.id)
        if not order:
            await message.answer("Sizda faol buyurtmalar topilmadi. Buyurtma berish uchun pastdagi tugmani bosing.")
            return

        lat = message.location.latitude
        lon = message.location.longitude
        await db.update_order_location(order["id"], lat, lon)

        out_param, prices_param = await _webapp_menu_params()
        welcome_kb = (
            kb.get_user_menu(out_param, prices_param)
            if str(message.from_user.id) != str(ADMIN_ID)
            else kb.get_main_menu(out_param, prices_param)
        )
        await message.answer(
            f"Joylashuvingiz muvaffaqiyatli tasdiqlandi! Buyurtmangiz tez orada yetkaziladi.\n\n"
            f"Buyurtma ID: #{order['id']}\n"
            f"Holati: <b>Kutish jarayonida</b>",
            reply_markup=welcome_kb,
            parse_mode="HTML"
        )

        # Notify admin group of updated address
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        admin_notify = (
            f"📍 <b>BUYURTMA #{order['id']} MANZILI YANGILANDI</b>\n\n"
            f"Mijoz: {html.escape(order['name'])}\n"
            f"Manzil: <a href='{maps_link}'>Xaritada ko'rish</a>"
        )
        await bot.send_message(
            GROUP_ID,
            admin_notify,
            parse_mode="HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
    except Exception:
        logger.exception("location_handler failed")
        await message.answer("Joylashuvni saqlashda xatolik yuz berdi.")

@router.message(F.text == "📦 Ombor boshqaruvi")
@router.message(Command("ombor"))
async def cmd_ombor(message: Message):
    is_admin = _is_admin(message.from_user.id)
    if not is_admin:
        print(f"Unauthorized ombor access: {message.from_user.id} vs {ADMIN_ID}")
        await message.answer(f"<b>Siz tizim administratori emassiz!</b>\nSizning Telegram ID: <code>{message.from_user.id}</code>")
        return
        
    inventory = await db.get_inventory()
    await message.answer("<b>Ombor zaxirasi holati:</b>\n\nKerakli mahsulotni tanlang:", reply_markup=kb.get_inventory_kb(inventory), parse_mode="HTML")

@router.message(F.text == "📊 Hisobotni olish")
@router.message(Command("hisobot"))
async def cmd_hisobot(message: Message):
    is_admin = _is_admin(message.from_user.id)
    if not is_admin:
        print(f"Unauthorized hisobot access: {message.from_user.id} vs {ADMIN_ID}")
        await message.answer(f"<b>Siz tizim administratori emassiz!</b>\nSizning Telegram ID: <code>{message.from_user.id}</code>")
        return
        
    await message.answer("<b>Tizim hisobotini olish:</b>\n\nKerakli hisobot turini tanlang:", reply_markup=kb.get_report_kb(), parse_mode="HTML")

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_callback(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Bu amal faqat admin uchun.", show_alert=True)
        return

    product_id = callback.data.replace("toggle_", "")
    await db.toggle_stock(product_id)
    inventory = await db.get_inventory()
    await callback.message.edit_reply_markup(reply_markup=kb.get_inventory_kb(inventory))
    await callback.answer("Holat o'zgardi")

@router.callback_query(F.data.startswith("order_"))
async def order_status_callback(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Bu amal faqat admin uchun.", show_alert=True)
        return

    parts = callback.data.split("_")
    if len(parts) != 3 or parts[1] not in {"accept", "reject"}:
        await callback.answer("Noto'g'ri amal.", show_alert=True)
        return
    action = parts[1]
    try:
        order_id = int(parts[2])
    except ValueError:
        await callback.answer("Noto'g'ri buyurtma ID.", show_alert=True)
        return
    
    status = "accepted" if action == "accept" else "rejected"
    status_text = "Qabul qilindi" if action == "accept" else "Rad etildi"
    order = await db.get_order_by_id(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return

    await db.update_order_status(order_id, status)
    
    new_text = callback.message.html_text + f"\n\n<b>Holati: {status_text}</b>"
    await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=None)

    try:
        if status == "accepted":
            products_pricing = await db.get_products_pricing()
            receipt = generate_thermal_receipt(order_id, order, products_pricing)
            customer_text = (
                f"<b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                f"Status: ⏳ Tayyorlanmoqda\n\n"
                f"🧾 <b>Sizning kvitansiyangiz:</b>\n"
                f"{receipt}"
            )
            customer_kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Yangi buyurtma berish", url="https://t.me/SaxovataBaraka_buyurtma_bot")]
                ]
            )
        else:
            customer_text = (
                f"<b>Uzr, buyurtmangiz qabul qilinmadi.</b>\n\n"
                f"Buyurtma ID: #{order_id}\n"
                f"Qo'shimcha ma'lumot olish uchun bog'lanishingiz mumkin:\n"
                f"Telefon: {html.escape(CONTACT_PHONE)}\n"
                f"Administrator: {html.escape(CONTACT_USERNAME)}"
            )
            tg_url = _contact_links()
            row = []
            if tg_url:
                row.append(InlineKeyboardButton(text="Telegram", url=tg_url))
            customer_kb = InlineKeyboardMarkup(inline_keyboard=[row]) if row else None

        await callback.bot.send_message(
            int(order["telegram_id"]),
            customer_text,
            parse_mode="HTML",
            reply_markup=customer_kb
        )
    except Exception:
        logger.exception("Failed to send order status message to customer for order_id=%s", order_id)

    await callback.answer(f"Buyurtma {status_text}")

@router.callback_query(F.data.startswith("report_"))
async def manual_report_callback(callback: CallbackQuery, bot: Bot):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Bu amal faqat admin uchun.", show_alert=True)
        return

    period = callback.data.replace("report_", "")
    if period not in {"daily", "monthly"}:
        await callback.answer("Noto'g'ri hisobot turi.", show_alert=True)
        return
    await callback.answer("Hisobot tayyorlanmoqda...")
    
    import reports as rep
    filename = None
    try:
        summary = await db.get_summary(period)
        if summary['count'] == 0:
            await callback.message.answer(f"Ushbu davr uchun ({period}) buyurtmalar topilmadi.")
            return

        text = (
            f"<b>{period.upper()} HISOBOT</b>\n\n"
            f"Buyurtmalar soni: {summary['count']} ta\n"
            f"Jami savdo: {summary['total_revenue']:,} so'm\n"
            f"Sof foyda: {summary['total_profit']:,} so'm"
        )
        
        filename = await rep.generate_excel_report(period)
        if filename:
            from aiogram.types import FSInputFile
            await bot.send_document(
                callback.from_user.id, 
                FSInputFile(filename), 
                caption=text, 
                parse_mode="HTML"
            )
        else:
            await callback.message.answer("Xatolik: Hisobot faylini yaratib bo'lmadi.")
    except Exception:
        logger.exception("manual_report_callback failed")
        await callback.message.answer("Xatolik: Hisobotni yaratishda muammo bo'ldi.")
    finally:
        if filename:
            try:
                import os
                os.remove(filename)
            except OSError:
                logger.warning("Failed to remove report file: %s", filename)

@router.inline_query()
async def inline_share_handler(inline_query: InlineQuery):
    photo_url = "https://muslim1313.github.io/bakery-bot-crm/assets/promo_share.png"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Botga o'tish va buyurtma berish", url="https://t.me/SaxovataBaraka_buyurtma_bot")]
        ]
    )
    
    result = InlineQueryResultPhoto(
        id="share_promo_1",
        photo_url=photo_url,
        thumbnail_url=photo_url,
        title="Botni do'stlarga ulashish",
        description="Saxovat Baraka shirinliklari",
        caption="<b>Saxovat Baraka</b> premium artisan pishiriqlari!\n\nEng mazali shirinliklarni bevosita Telegram Mini-App orqali buyurtma qiling. Do'stlaringizga ham ulashing.",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await inline_query.answer([result], cache_time=1, is_personal=True)

@router.message(Command("narx"))
async def cmd_narx(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ushbu amal faqat admin uchun.")
        return
        
    parts = message.text.split()
    if len(parts) < 4:
        inventory = await db.get_inventory()
        help_text = (
            "<b>Mahsulot narxini o'zgartirish buyrug'i:</b>\n\n"
            "Format: <code>/narx [Mahsulot_ID] [Tannarx] [Sotish_Narxi]</code>\n\n"
            "Mavjud Mahsulotlar va narxlar:\n"
        )
        for item in inventory:
            help_text += f"- <code>{item['product_id']}</code>: {item['product_name']} (Tannarx: {item['cost']:,} so'm, Sotish: {item['sell']:,} so'm)\n"
        
        help_text += "\nMisol: <code>/narx Pechini 1 38000 46000</code>"
        await message.answer(help_text, parse_mode="HTML")
        return

    try:
        sell = float(parts[-1])
        cost = float(parts[-2])
        product_id = " ".join(parts[1:-2])
        
        inventory = await db.get_inventory()
        existing_ids = [item["product_id"] for item in inventory]
        
        if product_id not in existing_ids:
            await message.answer(f"Xatolik: <code>{html.escape(product_id)}</code> nomli mahsulot topilmadi.", parse_mode="HTML")
            return
            
        await db.update_product_price(product_id, cost, sell)
        out_param, prices_param = await _webapp_menu_params()
        menu_kb = kb.get_main_menu(out_param, prices_param)
        await message.answer(
            f"Muvaffaqiyatli yangilandi!\n\n"
            f"Mahsulot: <b>{html.escape(product_id)}</b>\n"
            f"Yangi Tannarx: {cost:,} so'm\n"
            f"Yangi Sotish Narxi: {sell:,} so'm\n\n"
            f"Mini-appda yangi narx ko'rinishi uchun pastdagi "
            f"<b>Buyurtma berish</b> tugmasini qayta bosing yoki /start yuboring.",
            parse_mode="HTML",
            reply_markup=menu_kb,
        )
    except Exception:
        await message.answer("Xatolik: Narx formatini to'g'ri kiriting. Masalan: <code>/narx Pechini 1 38000 46000</code>", parse_mode="HTML")


def generate_thermal_receipt(order_id: int, order: dict, products_pricing: dict) -> str:
    from datetime import datetime
    import pytz
    tashkent_tz = pytz.timezone('Asia/Tashkent')
    
    created_at_str = order.get("created_at", "")
    try:
        if isinstance(created_at_str, str):
            dt = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = created_at_str
        dt_tashkent = dt.astimezone(tashkent_tz) if hasattr(dt, "astimezone") else dt
        date_formatted = dt_tashkent.strftime("%d.%m.%Y %H:%M")
    except Exception:
        date_formatted = datetime.now(tashkent_tz).strftime("%d.%m.%Y %H:%M")

    receipt = (
        "<code>"
        "================================\n"
        "        SAXOVAT BARAKA\n"
        "================================\n"
        f"Kvitansiya: #{order_id}\n"
        f"Sana:       {date_formatted}\n"
        f"Mijoz:      {order.get('name', 'Mijoz')}\n"
        f"Telefon:    {order.get('phone', '')}\n"
        f"Do'kon:     {order.get('store', '')}\n"
        "--------------------------------\n"
        "Mahsulotlar:\n"
    )
    
    try:
        cart = json.loads(order.get("cart_json", "{}"))
    except Exception:
        cart = {}

    for p_id, qty in cart.items():
        prod_info = products_pricing.get(p_id, {"name": p_id, "sell": 0})
        name = prod_info.get("name", p_id)
        sell_price = prod_info.get("sell", 0)
        item_total = sell_price * int(qty)
        
        name_short = name[:18]
        qty_str = f"{qty} d."
        price_str = f"{item_total:,} so'm"
        
        receipt += f"{name_short:<18} {qty_str:>5} {price_str:>8}\n"
        
    receipt += (
        "--------------------------------\n"
        f"JAMI:            {int(order.get('total_revenue', 0)):,} so'm\n"
        "================================\n"
        "    Xaridingiz uchun rahmat!\n"
        "================================"
        "</code>"
    )
    return receipt


@router.message(F.text == "📈 Tezkor Statistika")
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not _is_admin(message.from_user.id):
        await message.answer("Ushbu amal faqat admin uchun.")
        return

    try:
        stats = await db.get_admin_stats()
        
        today = stats["today"]
        yesterday = stats["yesterday"]
        month = stats["month"]
        top_products = stats["top_products"]
        
        target = 5_000_000
        progress = min(1.0, month["rev"] / target) if target > 0 else 0
        filled = int(progress * 10)
        bar = "█" * filled + "░" * (10 - filled)
        
        top_text = ""
        block_chars = ["█", "▆", "▄"]
        for idx, (p_id, qty) in enumerate(top_products):
            block = block_chars[idx] if idx < len(block_chars) else "■"
            top_text += f" {block} <code>{p_id:<12}</code>: {qty} dona\n"
            
        if not top_text:
            top_text = " Bugun hali savdo bo'lmadi.\n"

        stats_card = (
            "<b>📊 CRM TEZKOR STATISTIKA</b>\n\n"
            f"📅 <b>Bugungi holat:</b>\n"
            f"  • Buyurtmalar: {today['count']} ta\n"
            f"  • Savdo: <code>{int(today['rev']):,} so'm</code>\n"
            f"  • Sof Foyda: <code>{int(today['profit']):,} so'm</code>\n\n"
            f"⏮ <b>Kechagi holat:</b>\n"
            f"  • Buyurtmalar: {yesterday['count']} ta\n"
            f"  • Savdo: <code>{int(yesterday['rev']):,} so'm</code>\n"
            f"  • Sof Foyda: <code>{int(yesterday['profit']):,} so'm</code>\n\n"
            f"📆 <b>Joriy oylik:</b>\n"
            f"  • Buyurtmalar: {month['count']} ta\n"
            f"  • Savdo: <code>{int(month['rev']):,} so'm</code>\n"
            f"  • Sof Foyda: <code>{int(month['profit']):,} so'm</code>\n\n"
            f"🎯 <b>Haftalik Plan:</b>\n"
            f"  <code>{bar}</code> {int(progress * 100)}%\n"
            f"  (Plan: {target:,} so'm)\n\n"
            f"🏆 <b>Top sotilganlar (Bugun):</b>\n"
            f"{top_text}"
        )
        
        await message.answer(stats_card, parse_mode="HTML")
    except Exception as e:
        logger.exception("cmd_stats failed")
        await message.answer(f"Statistikani yuklashda xatolik: {e}")


@router.message(F.text == "📋 Buyurtmalarim")
@router.message(Command("buyurtmalar"))
async def cmd_buyurtmalar(message: Message):
    try:
        orders = await db.get_orders_by_user(message.from_user.id)
        if not orders:
            await message.answer("Sizda hali buyurtmalar mavjud emas.")
            return

        response_text = "<b>📋 Sizning oxirgi buyurtmalaringiz:</b>\n\n"
        
        status_map = {
            "pending": "⏳ Kutish jarayonida",
            "accepted": "✅ Qabul qilindi",
            "rejected": "❌ Rad etildi"
        }

        for order in orders:
            status_text = status_map.get(order.get("status"), order.get("status", "Kutishda"))
            
            created_at = order.get("created_at", "")
            try:
                if isinstance(created_at, str):
                    date_only = created_at.split()[0]
                else:
                    date_only = created_at.strftime("%Y-%m-%d")
            except Exception:
                date_only = ""

            response_text += (
                f"<b>Buyurtma #{order['id']}</b> ({date_only})\n"
                f"  Jami summa: {int(order['total_revenue']):,} so'm\n"
                f"  Holati: <b>{status_text}</b>\n"
                "--------------------------------\n"
            )

        await message.answer(response_text, parse_mode="HTML")
    except Exception as e:
        logger.exception("cmd_buyurtmalar failed")
        await message.answer(f"Buyurtmalarni yuklashda xatolik: {e}")
