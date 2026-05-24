from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import database as db
import reports as rep
from config import ADMIN_ID, GROUP_ID
from aiogram.types import FSInputFile
import logging
import os

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone='Asia/Tashkent')
    
    # Daily Report at 21:00
    scheduler.add_job(
        send_auto_report,
        CronTrigger(hour=21, minute=0),
        args=[bot, 'daily'],
        id='daily_report'
    )
    
    # Monthly Report on last day of month at 23:59
    scheduler.add_job(
        send_auto_report,
        CronTrigger(day='last', hour=23, minute=59),
        args=[bot, 'monthly'],
        id='monthly_report'
    )
    
    return scheduler

async def send_auto_report(bot, period):
    logging.info(f"Generating auto {period} report...")
    summary = await db.get_summary(period)
    
    if summary['count'] == 0:
        logging.info(f"No orders for {period} report. Skipping...")
        return

    text = (
        f"📊 <b>AVTOMATIK {period.upper()} HISOBOT</b>\n\n"
        f"✅ Buyurtmalar: {summary['count']} ta\n"
        f"💰 Jami savdo: {summary['total_revenue']:,} so'm\n"
        f"📈 Sof foyda: {summary['total_profit']:,} so'm\n\n"
        f"Batafsil ma'lumot Excel faylda 👇"
    )
    
    filename = await rep.generate_excel_report(period)
    recipient_id = GROUP_ID if GROUP_ID else ADMIN_ID
    if filename and recipient_id:
        try:
            await bot.send_document(
                recipient_id, 
                FSInputFile(filename), 
                caption=text, 
                parse_mode="HTML"
            )
            # Cleanup
            os.remove(filename)
        except Exception as e:
            logging.error(f"Failed to send auto report: {e}")
