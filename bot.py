import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat, MenuButtonDefault

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
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(router)
    
    # Setup Automation (Reports)
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    # Set Bot Commands
    common_commands = [
        BotCommand(command="start", description="Botni ishga tushirish")
    ]
    await bot.set_my_commands(common_commands, scope=BotCommandScopeDefault())
    
    if config.ADMIN_ID:
        try:
            admin_commands = [
                BotCommand(command="start", description="Botni ishga tushirish"),
                BotCommand(command="hisobot", description="Hisobotlar menyusi"),
                BotCommand(command="ombor", description="Ombor qoldig'ini boshqarish")
            ]
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=int(config.ADMIN_ID)))
        except Exception as e:
            logging.error(f"Failed to set admin commands: {e}")
    
    # Set menu button
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
        logging.info("Menu button set to default (Commands)")
    except Exception as e:
        logging.warning(f"Failed to set menu button: {e}")

    logging.info("Bot is starting...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
