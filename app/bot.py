"""Asosiy Bot - LOCAL API SUPPORT"""
import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode

from app.config import config
from app.database.db import Database
from app.services.cache import Cache
from app.services.downloader import Downloader
from app.handlers import start, download, admin
from app.middlewares.throttling import ThrottlingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

db = Database(config.db.dsn)
cache = Cache(config.redis.host, config.redis.port)
downloader = Downloader()


async def main():
    # LOCAL BOT API (2GB+ uchun)
    use_local = os.getenv('USE_LOCAL_API', 'false').lower() == 'true'

    if use_local:
        local_server = TelegramAPIServer.from_base("http://localhost:8081")
        logger.info("🚀 LOCAL BOT API ishlatilmoqda (2GB+ support)")

        bot = Bot(
            token=config.bot.token,
            server=local_server,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    else:
        logger.info("☁️ TELEGRAM SERVER ishlatilmoqda (2GB limit)")

        bot = Bot(
            token=config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    dp = Dispatcher()
    dp.message.middleware(ThrottlingMiddleware(config.throttle_rate))

    dp.include_router(start.router)
    dp.include_router(download.router)
    dp.include_router(admin.router)

    try:
        await db.connect()
        await cache.connect()
        logger.info("✅ Bot ishga tushdi!")

        dp['db'] = db
        dp['cache'] = cache
        dp['downloader'] = downloader
        dp['config'] = config

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Xato: {e}")
    finally:
        await db.disconnect()
        await cache.disconnect()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi")