"""Start Handler - PREMIUM VERSION"""
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message, db):
    try:
        user = message.from_user
        await db.add_user(user.id, user.username, user.first_name)

        text = (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>👋 Xush kelibsiz, {user.first_name}!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>🎬 Professional Video Downloader</b>\n\n"
            f"<b>Qo'llab-quvvatlanadigan platformalar:</b>\n"
            f"├ 🔴 YouTube\n"
            f"├ 📸 Instagram\n"
            f"├ 🎵 TikTok\n"
            f"└ 👥 Facebook\n\n"
            f"<b>📋 Qanday ishlaydi?</b>\n"
            f"1️⃣ Video havolasini yuboring\n"
            f"2️⃣ Sifatni tanlang (360p-1080p)\n"
            f"3️⃣ Bir soniyada yuklab oling\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 <b>Yordam:</b> /help\n"
            f"📊 <b>Statistika:</b> /stats\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )

        await message.answer(text)

    except Exception as e:
        logger.error(f"Start xato: {e}")
        await message.answer(
            "⚠️ <b>Texnik xatolik</b>\n\n"
            "Iltimos, qaytadan urinib ko'ring."
        )


@router.message(Command('help'))
async def cmd_help(message: Message):
    text = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>📖 Foydalanish qo'llanmasi</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>🎯 Asosiy funksiyalar:</b>\n\n"
        "<b>📥 Video yuklash:</b>\n"
        "• Havolani yuboring\n"
        "• Sifatni tanlang\n"
        "• Videoni oling\n\n"
        "<b>⚡️ Qo'llab-quvvatlanadigan sifatlar:</b>\n"
        "• 360p - Tezkor yuklash\n"
        "• 480p - Standart sifat\n"
        "• 720p - HD sifat\n"
        "• 1080p - Full HD\n\n"
        "<b>🔒 Maxfiylik:</b>\n"
        "• Sizning ma'lumotlaringiz xavfsiz\n"
        "• Videolar avtomatik o'chiriladi\n"
        "• Tarix saqlanmaydi\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "<b>🎯 Komandalar:</b>\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Bu yordam sahifasi\n"
        "/stats - Sizning statistikangiz\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💬 <b>Savol yoki muammolar?</b>\n"
        "Yordam: /help"
    )
    await message.answer(text)


@router.message(Command('stats'))
async def cmd_stats(message: Message, db):
    try:
        stats = await db.get_stats()

        text = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>📊 Bot Statistikasi</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "<b>👥 FOYDALANUVCHILAR</b>\n"
            f"├ Jami: <code>{stats.get('total_users', 0):,}</code>\n"
            f"├ Bugun: <code>{stats.get('new_today', 0)}</code>\n"
            f"└ Faol (7 kun): <code>{stats.get('active_weekly', 0)}</code>\n\n"
            "<b>📥 YUKLASHLAR</b>\n"
            f"├ Jami: <code>{stats.get('total_downloads', 0):,}</code>\n"
            f"└ Bugun: <code>{stats.get('downloads_today', 0)}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡️ <b>Tezkor. Ishonchli. Professional.</b>"
        )

        await message.answer(text)

    except Exception as e:
        logger.error(f"Stats xato: {e}")
        await message.answer(
            "⚠️ <b>Statistikani yuklab bo'lmadi</b>\n\n"
            "Iltimos, keyinroq qaytadan urinib ko'ring."
        )