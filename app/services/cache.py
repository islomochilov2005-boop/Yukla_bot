"""Redis Cache - Aiogram 3.24.0"""
import redis.asyncio as redis
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        try:
            self.client = await redis.from_url(
                f"redis://{self.host}:{self.port}",
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            logger.info("✅ Redis ulandi")
        except Exception as e:
            logger.warning(f"⚠️ Redis xato: {e}")
            self.client = None

    async def disconnect(self):
        if self.client:
            await self.client.close()

    # VIDEO INFO CACHE
    async def get(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = await self.client.get(f"video:{key}")
            return json.loads(data) if data else None
        except:
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        if not self.client:
            return
        try:
            await self.client.setex(
                f"video:{key}",
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except:
            pass

    # FILE_ID CACHE (MUHIM!)
    async def get_file_id(self, url: str, quality: str) -> Optional[str]:
        """Telegram file_id ni olish"""
        if not self.client:
            return None
        try:
            key = f"file:{url}:{quality}"
            return await self.client.get(key)
        except:
            return None

    async def set_file_id(self, url: str, quality: str, file_id: str, ttl: int = 86400):
        """Telegram file_id ni saqlash (24 soat)"""
        if not self.client:
            return
        try:
            key = f"file:{url}:{quality}"
            await self.client.setex(key, ttl, file_id)
            logger.info(f"✅ File ID saqlandi: {quality}")
        except Exception as e:
            logger.error(f"File ID saqlash xato: {e}")