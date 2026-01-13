"""Yordamchi funksiyalar"""
import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.config import TEMP_DIR, AUTO_DELETE_TEMP

logger = logging.getLogger(__name__)


def format_bytes(bytes_num: int) -> str:
    """
    Baytlarni o'qish mumkin bo'lgan formatga o'zgartirish

    Args:
        bytes_num: Bayt soni

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} PB"


def format_duration(seconds: int) -> str:
    """
    Sekundlarni vaqt formatiga o'zgartirish

    Args:
        seconds: Sekund

    Returns:
        Formatted time (e.g., "1:23:45")
    """
    if not seconds or seconds < 0:
        return "0:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_number(num: int) -> str:
    """
    Raqamlarni qisqa formatga o'zgartirish

    Args:
        num: Raqam

    Returns:
        Formatted number (e.g., "1.5M")
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


async def cleanup_temp_files(max_age_hours: int = 1):
    """
    Eski temp fayllarni tozalash

    Args:
        max_age_hours: Fayl yoshining maksimal limiti (soat)
    """
    if not AUTO_DELETE_TEMP:
        return

    try:
        now = datetime.now()
        deleted = 0

        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)

            # Fayl ekanligini tekshirish
            if not os.path.isfile(filepath):
                continue

            # Fayl yoshini tekshirish
            file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))

            if file_age > timedelta(hours=max_age_hours):
                try:
                    os.remove(filepath)
                    deleted += 1
                except Exception as e:
                    logger.error(f"Faylni o'chirishda xato {filepath}: {e}")

        if deleted > 0:
            logger.info(f"🗑️  {deleted} ta eski fayl o'chirildi")

    except Exception as e:
        logger.error(f"Temp cleanup xato: {e}")


async def periodic_cleanup():
    """Davriy tozalash"""
    while True:
        try:
            await asyncio.sleep(1800)  # Har 30 daqiqada
            await cleanup_temp_files()
        except Exception as e:
            logger.error(f"Periodic cleanup xato: {e}")


def validate_url(url: str) -> bool:
    """
    URL ni validatsiya qilish

    Args:
        url: Tekshiriladigan URL

    Returns:
        True agar to'g'ri bo'lsa
    """
    if not url or len(url) < 10:
        return False

    # Asosiy tekshirish
    if not url.startswith(('http://', 'https://')):
        return False

    # Xavfli belgilarni tekshirish
    dangerous_chars = ['<', '>', '"', "'", ';']
    if any(char in url for char in dangerous_chars):
        return False

    return True


def get_platform_emoji(platform: str) -> str:
    """
    Platforma uchun emoji olish

    Args:
        platform: Platforma nomi

    Returns:
        Emoji string
    """
    emojis = {
        'youtube': '▶️',
        'instagram': '📸',
        'tiktok': '🎵',
        'facebook': '👥',
        'twitter': '🐦',
    }
    return emojis.get(platform.lower(), '🎬')


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Matnni qisqartirish

    Args:
        text: Asl matn
        max_length: Maksimal uzunlik
        suffix: Oxiriga qo'shiladigan belgi

    Returns:
        Qisqartirilgan matn
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def escape_html(text: str) -> str:
    """
    HTML maxsus belgilarini escape qilish

    Args:
        text: Asl matn

    Returns:
        Escaped matn
    """
    if not text:
        return ""

    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


async def safe_delete_message(message, delay: Optional[int] = None):
    """
    Xabarni xavfsiz o'chirish

    Args:
        message: O'chiriladigan xabar
        delay: Kechikish (sekundlarda)
    """
    try:
        if delay:
            await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.debug(f"Xabarni o'chirib bo'lmadi: {e}")


def get_error_message(error: Exception) -> str:
    """
    Xato haqida foydalanuvchiga tushunarli xabar

    Args:
        error: Exception obyekti

    Returns:
        Xabar matni
    """
    error_messages = {
        'ConnectionError': '🌐 Internet bilan bog\'lanishda muammo',
        'TimeoutError': '⏱️ Vaqt tugadi, qaytadan urinib ko\'ring',
        'PermissionError': '🔒 Ruxsat yo\'q',
        'FileNotFoundError': '📁 Fayl topilmadi',
        'MemoryError': '💾 Xotira yetarli emas'
    }

    error_type = type(error).__name__
    return error_messages.get(error_type, '❌ Kutilmagan xatolik yuz berdi')


class ProgressTracker:
    """Yuklash jarayonini kuzatish"""

    def __init__(self, total: int, message=None):
        self.total = total
        self.current = 0
        self.message = message
        self.last_update = 0

    async def update(self, increment: int = 1):
        """Progress ni yangilash"""
        self.current += increment
        percentage = (self.current / self.total) * 100

        # Har 10% da yangilash
        if percentage - self.last_update >= 10 and self.message:
            try:
                await self.message.edit_text(
                    f"⏬ Yuklanmoqda... {percentage:.0f}%"
                )
                self.last_update = percentage
            except:
                pass

    def is_complete(self) -> bool:
        """Tugaganligini tekshirish"""
        return self.current >= self.total