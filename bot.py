import asyncio
import logging
from aiogram import Bot, Dispatcher

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat, MenuButtonDefault
from aiogram.exceptions import TelegramConflictError

import config
from handlers import router
from database import init_db
from scheduler import setup_scheduler

async def main():
    # Logging setup
    logging.basicConfig(level=logging.INFO)
    
    if not config.BOT_TOKEN:
        logging.error("BOT_TOKEN is missing in .env or config.py!")
        return

    # Init DB
    await init_db()
    
    # Init Bot and Dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(router)
    
    # Setup Automation (Reports)
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    # Set Bot Commands
    common_commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="buyurtmalar", description="Buyurtmalarim tarixi")
    ]
    await bot.set_my_commands(common_commands, scope=BotCommandScopeDefault())
    
    if config.ADMIN_ID:
        try:
            admin_commands = [
                BotCommand(command="start", description="Botni ishga tushirish"),
                BotCommand(command="hisobot", description="Hisobotlar menyusi"),
                BotCommand(command="ombor", description="Ombor qoldig'ini boshqarish"),
                BotCommand(command="narx", description="Mahsulot narxini o'zgartirish"),
                BotCommand(command="stats", description="Tezkor statistika paneli"),
                BotCommand(command="buyurtmalar", description="Buyurtmalarim tarixi")
            ]
            for admin_id_str in config.ADMIN_ID.split(","):
                try:
                    admin_id_clean = admin_id_str.strip()
                    if admin_id_clean.isdigit() or (admin_id_clean.startswith("-") and admin_id_clean[1:].isdigit()):
                        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=int(admin_id_clean)))
                        logging.info(f"Registered admin commands for ID: {admin_id_clean}")
                except Exception as scope_err:
                    logging.error(f"Failed to set admin commands for single ID {admin_id_str}: {scope_err}")
        except Exception as e:
            logging.error(f"Failed to set admin commands: {e}")
    
    # Set menu button
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
        logging.info("Menu button set to default (Commands)")
    except Exception as e:
        logging.warning(f"Failed to set menu button: {e}")

    logging.info("Bot is starting...")
    
    await bot.delete_webhook(drop_pending_updates=False)
    try:
        await dp.start_polling(bot)
    except TelegramConflictError:
        logging.error(
            "Polling conflict: boshqa instansiya allaqachon getUpdates ishlatyapti. "
            "Iltimos botni faqat bitta joyda ishga tushiring."
        )
    finally:
        from database import close_db
        await close_db()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
