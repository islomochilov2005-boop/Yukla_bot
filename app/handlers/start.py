"""Start Handler - ULTRA PREMIUM DESIGN"""
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
            f"<b>👋 Xush kelibsiz, {user.first_name}!</b>\n\n"
            f"<b>🎬 Professional Video Downloader</b>\n\n"
            f"<b>Qo'llab-quvvatlanadi:</b>\n"
            f"🔴 YouTube\n"
            f"📸 Instagram\n"
            f"🎵 TikTok\n"
            f"👥 Facebook\n\n"
            f"<b>📋 Qanday ishlaydi?</b>\n"
            f"1️⃣ Video havolasini yuboring\n"
            f"2️⃣ Video yoki Audio tanlang\n"
            f"3️⃣ Sifatni tanlang\n"
            f"4️⃣ Bir soniyada oling\n\n"
            f"💡 <b>Yordam:</b> /help\n"
            f"📊 <b>Statistika:</b> /stats"
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
        "<b>📖 Foydalanish Qo'llanmasi</b>\n\n"
        "<b>🎯 Asosiy Funksiyalar</b>\n\n"
        "<b>📥 Video yuklash:</b>\n"
        "• Havolani yuboring\n"
        "• Formatni tanlang (Video/Audio)\n"
        "• Sifatni tanlang\n"
        "• Yuklab oling\n\n"
        "<b>⚡️ Sifatlar:</b>\n"
        "• 360p - Tezkor\n"
        "• 480p - Standart\n"
        "• 720p - HD\n"
        "• 1080p - Full HD\n"
        "• MP3 - Audio\n\n"
        "<b>🔒 Maxfiylik:</b>\n"
        "• Ma'lumotlaringiz xavfsiz\n"
        "• Fayllar avtomatik o'chiriladi\n"
        "• Tarix saqlanmaydi\n\n"
        "<b>🎯 Komandalar</b>\n"
        "/start - Qayta boshlash\n"
        "/help - Yordam\n"
        "/stats - Statistika"
    )
    await message.answer(text)


@router.message(Command('stats'))
async def cmd_stats(message: Message, db):
    try:
        stats = await db.get_stats()

        text = (
            "<b>📊 Bot Statistikasi</b>\n\n"
            "<b>👥 FOYDALANUVCHILAR</b>\n"
            f"Jami: <code>{stats.get('total_users', 0):,}</code>\n"
            f"Bugun: <code>{stats.get('new_today', 0)}</code>\n"
            f"Faol: <code>{stats.get('active_weekly', 0)}</code>\n\n"
            "<b>📥 YUKLASHLAR</b>\n"
            f"Jami: <code>{stats.get('total_downloads', 0):,}</code>\n"
            f"Bugun: <code>{stats.get('downloads_today', 0)}</code>\n\n"
            "⚡️ <b>Tezkor • Ishonchli • Professional</b>"
        )

        await message.answer(text)

    except Exception as e:
        logger.error(f"Stats xato: {e}")
        await message.answer(
            "⚠️ <b>Statistikani yuklab bo'lmadi</b>\n\n"
            "Keyinroq qaytadan urinib ko'ring."
        )