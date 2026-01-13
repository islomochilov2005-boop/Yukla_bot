"""Database - Aiogram 3.24.0"""
import asyncpg
import logging
from typing import Optional
from datetime import datetime, timedelta
from .models import CREATE_TABLES

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            await self.create_tables()
            logger.info("✅ PostgreSQL ulandi")
        except Exception as e:
            logger.error(f"❌ PostgreSQL xato: {e}")
            raise

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute(CREATE_TABLES)

    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username, first_name)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO UPDATE SET last_active = NOW()
                """, user_id, username, first_name)
        except Exception as e:
            logger.error(f"User xato: {e}")

    async def add_download(self, user_id: int, platform: str, quality: str,
                           file_size: int = None, success: bool = True):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO downloads (user_id, platform, quality, file_size, success)
                    VALUES ($1, $2, $3, $4, $5)
                """, user_id, platform, quality, file_size, success)
        except Exception as e:
            logger.error(f"Download xato: {e}")

    async def get_stats(self):
        try:
            async with self.pool.acquire() as conn:
                today = datetime.now().date()
                week_ago = today - timedelta(days=7)

                row = await conn.fetchrow("""
                    SELECT 
                        (SELECT COUNT(*) FROM users) as total_users,
                        (SELECT COUNT(*) FROM users WHERE join_date::date = $1) as new_today,
                        (SELECT COUNT(DISTINCT user_id) FROM downloads WHERE date >= $2) as active_weekly,
                        (SELECT COUNT(*) FROM downloads WHERE success = TRUE) as total_downloads,
                        (SELECT COUNT(*) FROM downloads WHERE date::date = $1) as downloads_today
                """, today, week_ago)

                return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Stats xato: {e}")
            return {}

    # URL MAPPING (callback_data qisqartirish)
    async def save_url(self, url: str) -> int:
        """URL ni saqlash va ID olish"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    INSERT INTO url_mappings (url)
                    VALUES ($1)
                    ON CONFLICT (url) DO UPDATE SET url = EXCLUDED.url
                    RETURNING id
                """, url)
                return row['id']
        except Exception as e:
            logger.error(f"URL saqlash xato: {e}")
            return None

    async def get_url(self, url_id: int) -> Optional[str]:
        """ID bo'yicha URL olish"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT url FROM url_mappings WHERE id = $1", url_id
                )
                return row['url'] if row else None
        except Exception as e:
            logger.error(f"URL olish xato: {e}")
            return None