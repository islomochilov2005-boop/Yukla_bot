"""Download Handler - PREMIUM DESIGN"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import re
import os
import asyncio
import logging

logger = logging.getLogger(__name__)
router = Router()

URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


@router.message(F.text.regexp(URL_PATTERN))
async def handle_url(message: Message, downloader, cache, db):
    """URL handler - PREMIUM"""
    try:
        urls = URL_PATTERN.findall(message.text)
        if not urls:
            return

        url = urls[0]

        # URL ni bazaga saqlash
        url_id = await db.save_url(url)
        if not url_id:
            await message.answer(
                "⚠️ <b>Xatolik</b>\n\n"
                "Iltimos, qaytadan urinib ko'ring."
            )
            return

        # Cache tekshirish
        cached = await cache.get(url)
        if cached:
            from app.keyboards.inline import get_quality_keyboard
            await message.answer(
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>📹 {cached['title']}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⏱ <b>Davomiyligi:</b> {cached['duration']}\n"
                f"👁 <b>Ko'rishlar:</b> {cached['views']}\n"
                f"📢 <b>Kanal:</b> {cached['uploader']}\n\n"
                f"<b>Sifatni tanlang:</b>",
                reply_markup=get_quality_keyboard(url_id)
            )
            return

        # Tahlil qilinmoqda
        status = await message.answer(
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>⏳ Tahlil qilinmoqda...</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Video ma'lumotlari yuklanmoqda."
        )

        info = await downloader.get_info(url)

        if not info:
            await status.edit_text(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<b>❌ Video topilmadi</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "<b>Mumkin bo'lgan sabablar:</b>\n"
                "├ Noto'g'ri havola\n"
                "├ Video yopiq (private)\n"
                "└ Video o'chirilgan\n\n"
                "💡 <b>Maslahat:</b> Havolani qayta tekshiring"
            )
            return

        # Cache ga saqlash
        await cache.set(url, info)

        from app.keyboards.inline import get_quality_keyboard
        await status.edit_text(
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>✅ Tayyor!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>📹 {info['title']}</b>\n\n"
            f"⏱ <b>Davomiyligi:</b> {info['duration']}\n"
            f"👁 <b>Ko'rishlar:</b> {info['views']}\n"
            f"📢 <b>Kanal:</b> {info['uploader']}\n\n"
            f"<b>Sifatni tanlang:</b>",
            reply_markup=get_quality_keyboard(url_id)
        )

    except Exception as e:
        logger.error(f"URL handler xato: {e}", exc_info=True)
        try:
            await message.answer(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<b>⚠️ Texnik xatolik</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Iltimos, qaytadan urinib ko'ring."
            )
        except:
            pass


@router.callback_query(F.data.startswith('dl:'))
async def process_download(callback: CallbackQuery, downloader, db, cache):
    """Video yuklash - PREMIUM"""
    try:
        await callback.answer("⚡️ Yuklanmoqda...")

        parts = callback.data.split(':')
        if len(parts) != 3:
            await callback.message.edit_text("❌ Noto'g'ri format!")
            return

        url_id, quality = int(parts[1]), parts[2]

        # URL ni olish
        url = await db.get_url(url_id)
        if not url:
            await callback.message.edit_text(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<b>❌ Xatolik</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Havola topilmadi.\n"
                "Qaytadan urinib ko'ring."
            )
            return

        # FILE_ID CACHE (TEZKOR!)
        file_id = await cache.get_file_id(url, quality)

        if file_id:
            logger.info(f"✅ Cache: {quality}")
            try:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="📢 Botni Ulashish",
                        url="https://t.me/share/url?url=https://t.me/your_bot"
                    )]
                ])

                await callback.message.answer_video(
                    video=file_id,
                    caption=(
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"<b>✅ Muvaffaqiyatli!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"<b>Sifat:</b> {quality}\n"
                        f"<b>Status:</b> ⚡️ Cache dan yuborildi\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 Do'stlaringizga ulashing!"
                    ),
                    reply_markup=keyboard
                )
                await callback.message.delete()

                await db.add_download(
                    user_id=callback.from_user.id,
                    platform=downloader._get_platform(url),
                    quality=quality,
                    success=True
                )
                return
            except Exception as e:
                logger.warning(f"Cache xato: {e}")

        # YUKLASH
        msg = await callback.message.edit_text(
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>⏬ Yuklanmoqda...</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Sifat:</b> {quality}\n"
            "<b>Status:</b> Serverdan yuklanmoqda\n\n"
            "⏳ Iltimos kuting..."
        )

        result = await downloader.download(url, quality)

        if not result:
            await msg.edit_text(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<b>❌ Yuklash muvaffaqiyatsiz</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "<b>Mumkin bo'lgan sabablar:</b>\n"
                "├ Video hajmi 2GB dan katta\n"
                "├ Internet bilan muammo\n"
                "└ Server xatosi\n\n"
                "💡 <b>Yechim:</b>\n"
                "• Pastroq sifat tanlang\n"
                "• Qaytadan urinib ko'ring"
            )
            await db.add_download(
                user_id=callback.from_user.id,
                platform=downloader._get_platform(url),
                quality=quality,
                success=False
            )
            return

        filepath, file_size = result

        await msg.edit_text(
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<b>📤 Yuborilmoqda...</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<b>Hajmi:</b> {file_size / 1_000_000:.1f} MB\n"
            "<b>Status:</b> Telegram ga yuklanmoqda"
        )

        video = FSInputFile(filepath)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📢 Botni Ulashish",
                url="https://t.me/share/url?url=https://t.me/your_bot"
            )]
        ])

        sent_message = await callback.message.answer_video(
            video=video,
            caption=(
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>✅ Muvaffaqiyatli!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"<b>Sifat:</b> {quality}\n"
                f"<b>Hajmi:</b> {file_size / 1_000_000:.1f} MB\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Do'stlaringizga ulashing!"
            ),
            reply_markup=keyboard
        )

        # FILE_ID CACHE
        if sent_message.video:
            await cache.set_file_id(url, quality, sent_message.video.file_id)

        await msg.delete()
        await callback.message.delete()

        await db.add_download(
            user_id=callback.from_user.id,
            platform=downloader._get_platform(url),
            quality=quality,
            file_size=file_size,
            success=True
        )

        asyncio.create_task(cleanup_file(filepath))

    except Exception as e:
        logger.error(f"Download xato: {e}", exc_info=True)
        try:
            await callback.message.edit_text(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "<b>⚠️ Kutilmagan xatolik</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Iltimos, qaytadan urinib ko'ring."
            )
        except:
            pass


@router.callback_query(F.data == 'cancel')
async def cancel(callback: CallbackQuery):
    """Bekor qilish"""
    try:
        await callback.message.delete()
        await callback.answer("✅ Bekor qilindi")
    except:
        pass


async def cleanup_file(filepath: str):
    """Fayl tozalash"""
    await asyncio.sleep(300)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"🗑️ Tozalandi: {filepath}")
    except Exception as e:
        logger.error(f"Cleanup xato: {e}")