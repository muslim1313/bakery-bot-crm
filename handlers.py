from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions, InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import ADMIN_ID, GROUP_ID, PRODUCTS_PRICING
import database as db
import keyboards as kb
import json
import html
import logging

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

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    # Get inventory to handle out-of-stock
    try:
        inventory = await db.get_inventory()
        out_of_stock_ids = [item["product_id"] for item in inventory if not item["in_stock"]]
        out_param = ",".join(out_of_stock_ids)
    except Exception as e:
        print(f"DB Error in start: {e}")
        out_param = ""

    welcome_text = (
        "✨ <b>Saxovat Baraka</b> buyurtma botiga xush kelibsiz!\n\n"
        "👇 Buyurtma berish uchun pastdagi tugmani bosing."
    )
    
    # Check admin status
    is_admin = str(message.from_user.id) == str(ADMIN_ID)
    
    if is_admin:
        reply_markup = kb.get_main_menu(out_param)
    else:
        reply_markup = kb.get_user_menu(out_param)

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
            await message.answer("⚠️ Savatcha bo'sh yoki noto'g'ri.")
            return

        phone = _normalize_text(data.get("phone"), "Noma'lum")
        client_name = _normalize_text(data.get("name"), message.from_user.full_name or "Noma'lum")
        store_name = _normalize_text(data.get("store"), "Noma'lum")
        lat = _parse_float(data.get("lat"))
        lon = _parse_float(data.get("lon"))

        total_cost = 0
        total_revenue = 0
        order_details = ""
        clean_cart = {}

        inventory = await db.get_inventory()
        stock_map = {item["product_id"]: bool(item["in_stock"]) for item in inventory}

        for p_id, qty in cart.items():
            product = PRODUCTS_PRICING.get(p_id)
            if not product:
                continue

            try:
                qty_int = int(qty)
            except (TypeError, ValueError):
                continue

            if qty_int < 1 or qty_int > MAX_QTY_PER_ITEM:
                continue

            if not stock_map.get(p_id, True):
                await message.answer(f"⚠️ {product['name']} hozir omborda yo'q. Iltimos savatchani yangilang.")
                return

            clean_cart[p_id] = qty_int
            cost = product["cost"] * qty_int
            sell = product["sell"] * qty_int
            total_cost += cost
            total_revenue += sell
            order_details += f"▫️ {product['name']}: {qty_int} dona\n"

        if not clean_cart:
            await message.answer("⚠️ Savatchada yaroqli mahsulot topilmadi.")
            return

        profit = total_revenue - total_cost

        # Save to DB
        order_id = await db.add_order(
            message.from_user.id, client_name, phone, store_name, lat, lon, clean_cart,
            total_cost, total_revenue, profit
        )

        # Send info to User
        await message.answer(
            f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
            f"ID: #{order_id}\n"
            f"Jami: {total_revenue:,} so'm\n\n"
            f"Tez orada operatorimiz siz bilan bog'lanadi.",
            parse_mode="HTML"
        )

        # Send Order Card to Group/Admin
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        admin_card = (
            f"🔔 <b>YANGI BUYURTMA #{order_id}</b>\n\n"
            f"👤 Mijoz: {html.escape(client_name)}\n"
            f"📞 Tel: <code>{html.escape(phone)}</code>\n"
            f"🏪 Do'kon: {html.escape(store_name)}\n"
        )
        
        if lat is not None and lon is not None:
            admin_card += f"📍 Manzil: <a href='{maps_link}'>Xaritada ko'rish</a>\n\n"
        else:
            admin_card += "📍 Manzil: Yuborilmagan\n\n"

        admin_card += (
            f"📦 <b>Mahsulotlar:</b>\n{order_details}\n"
            f"💰 Jami: {total_revenue:,} so'm\n"
            f"📈 Foyda: {profit:,} so'm"
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

@router.message(F.text == "📦 Ombor boshqaruvi")
@router.message(Command("ombor"))
async def cmd_ombor(message: Message):
    is_admin = _is_admin(message.from_user.id)
    if not is_admin:
        print(f"Unauthorized ombor access: {message.from_user.id} vs {ADMIN_ID}")
        await message.answer(f"⚠️ <b>Siz admin emassiz!</b>\nSizning ID: <code>{message.from_user.id}</code>\nUshbu IDni admin sifatida ro'yxatdan o'tkazing.")
        return
        
    inventory = await db.get_inventory()
    await message.answer("📦 <b>Ombor holati:</b>\n\nKerakli mahsulotni tanlang:", reply_markup=kb.get_inventory_kb(inventory), parse_mode="HTML")

@router.message(F.text == "📊 Hisobotni olish")
@router.message(Command("hisobot"))
async def cmd_hisobot(message: Message):
    is_admin = _is_admin(message.from_user.id)
    if not is_admin:
        print(f"Unauthorized hisobot access: {message.from_user.id} vs {ADMIN_ID}")
        await message.answer(f"⚠️ <b>Siz admin emassiz!</b>\nSizning ID: <code>{message.from_user.id}</code>")
        return
        
    await message.answer("📊 <b>Hisobot turini tanlang:</b>", reply_markup=kb.get_report_kb(), parse_mode="HTML")

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
    status_text = "✅ Qabul qilindi" if action == "accept" else "❌ Rad etildi"
    
    await db.update_order_status(order_id, status)
    
    new_text = callback.message.html_text + f"\n\n🏁 <b>Status: {status_text}</b>"
    await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=None)
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
            await callback.message.answer(f"⚠️ Bu davr uchun ({period}) buyurtmalar topilmadi.")
            return

        text = (
            f"📊 <b>{period.upper()} HISOBOT</b>\n\n"
            f"✅ Buyurtmalar: {summary['count']} ta\n"
            f"💰 Jami savdo: {summary['total_revenue']:,} so'm\n"
            f"📈 Sof foyda: {summary['total_profit']:,} so'm"
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
            [InlineKeyboardButton(text="🛒 Botga o'tish va buyurtma berish", url="https://t.me/SaxovataBaraka_buyurtma_bot")]
        ]
    )
    
    result = InlineQueryResultPhoto(
        id="share_promo_1",
        photo_url=photo_url,
        thumbnail_url=photo_url,
        title="Botni do'stlarga ulashish",
        description="Saxovat Baraka shirinliklari",
        caption="✨ <b>Saxovat Baraka</b> pishiriqlari!\n\nEng mazali va hamyonbop shirinliklarni bevosita bot orqali buyurtma qiling. Do'stlaringizga ham ulashing! 🍪",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await inline_query.answer([result], cache_time=1, is_personal=True)

