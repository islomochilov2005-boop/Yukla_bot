"""Download Handler - AUDIO/VIDEO SUPPORT"""
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
    """URL handler"""
    try:
        urls = URL_PATTERN.findall(message.text)
        if not urls:
            return

        url = urls[0]

        # URL ni saqlash
        url_id = await db.save_url(url)
        if not url_id:
            await message.answer("⚠️ <b>Xatolik</b>\n\nQaytadan urinib ko'ring.")
            return

        # Cache
        cached = await cache.get(url)
        if cached:
            from app.keyboards.inline import get_format_keyboard
            await message.answer(
                f"<b>📹 {cached['title']}</b>\n\n"
                f"⏱ <b>Davomiyligi:</b> {cached['duration']}\n"
                f"👁 <b>Ko'rishlar:</b> {cached['views']}\n"
                f"📢 <b>Kanal:</b> {cached['uploader']}\n\n"
                f"<b>Formatni tanlang:</b>",
                reply_markup=get_format_keyboard(url_id)
            )
            return

        # Ma'lumot olish
        status = await message.answer("<b>⏳ Tahlil qilinmoqda...</b>")

        info = await downloader.get_info(url)

        if not info:
            await status.edit_text(
                "<b>❌ Video topilmadi</b>\n\n"
                "<b>Sabablar:</b>\n"
                "• Noto'g'ri havola\n"
                "• Video yopiq\n"
                "• Video o'chirilgan"
            )
            return

        await cache.set(url, info)

        from app.keyboards.inline import get_format_keyboard
        await status.edit_text(
            f"<b>✅ Tayyor!</b>\n\n"
            f"<b>📹 {info['title']}</b>\n\n"
            f"⏱ <b>Davomiyligi:</b> {info['duration']}\n"
            f"👁 <b>Ko'rishlar:</b> {info['views']}\n"
            f"📢 <b>Kanal:</b> {info['uploader']}\n\n"
            f"<b>Formatni tanlang:</b>",
            reply_markup=get_format_keyboard(url_id)
        )

    except Exception as e:
        logger.error(f"URL xato: {e}", exc_info=True)
        try:
            await message.answer(
                "<b>⚠️ Texnik xatolik</b>\n\n"
                "Iltimos, qaytadan urinib ko'ring."
            )
        except:
            pass


@router.callback_query(F.data.startswith('format:'))
async def select_format(callback: CallbackQuery, db):
    """Video yoki Audio tanlash - YANGI!"""
    try:
        parts = callback.data.split(':')
        url_id, format_type = int(parts[1]), parts[2]

        if format_type == 'audio':
            # Audio tanlandi - to'g'ridan-to'g'ri yuklash
            await callback.answer("🎵 Audio yuklanmoqda...")
            await process_audio_download(callback, url_id, db)
        else:
            # Video tanlandi - sifat tanlash
            await callback.answer("📹 Sifatni tanlang")
            from app.keyboards.inline import get_quality_keyboard
            await callback.message.edit_text(
                "<b>📹 Video sifatini tanlang:</b>",
                reply_markup=get_quality_keyboard(url_id)
            )
    except Exception as e:
        logger.error(f"Format select xato: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


async def process_audio_download(callback: CallbackQuery, url_id: int, db):
    """Audio yuklash"""
    try:
        url = await db.get_url(url_id)
        if not url:
            await callback.message.edit_text("<b>❌ Havola topilmadi</b>")
            return

        # Audio yuklash funksiyasi kerak
        from app.services.downloader import Downloader
        downloader = Downloader()

        msg = await callback.message.edit_text(
            "<b>⏬ Audio yuklanmoqda...</b>\n\n"
            "<b>Format:</b> MP3\n"
            "<b>Status:</b> Yuklanmoqda"
        )

        # Audio yuklash (keyingi qadamda qo'shamiz)
        result = await downloader.download_audio(url)

        if not result:
            await msg.edit_text(
                "<b>❌ Yuklash muvaffaqiyatsiz</b>\n\n"
                "Qaytadan urinib ko'ring."
            )
            return

        filepath, file_size, filename = result

        await msg.edit_text("<b>📤 Yuborilmoqda...</b>")

        audio = FSInputFile(filepath, filename=filename)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📢 Botni Ulashish",
                url="https://t.me/share/url?url=https://t.me/your_bot"
            )]
        ])

        await callback.message.answer_audio(
            audio=audio,
            title=filename.replace('.mp3', ''),
            caption=(
                f"<b>✅ Tayyor!</b>\n\n"
                f"<b>Format:</b> MP3\n"
                f"<b>Hajmi:</b> {file_size / 1_000_000:.1f} MB"
            ),
            reply_markup=keyboard
        )

        await msg.delete()
        await callback.message.delete()

        # Cleanup
        asyncio.create_task(cleanup_file(filepath))

    except Exception as e:
        logger.error(f"Audio download xato: {e}")
        await callback.message.edit_text("<b>⚠️ Xatolik</b>")


@router.callback_query(F.data.startswith('dl:'))
async def process_download(callback: CallbackQuery, downloader, db, cache):
    """Video yuklash"""
    try:
        await callback.answer("⚡️ Yuklanmoqda...")

        parts = callback.data.split(':')
        url_id, quality = int(parts[1]), parts[2]

        url = await db.get_url(url_id)
        if not url:
            await callback.message.edit_text("<b>❌ Havola topilmadi</b>")
            return

        # FILE_ID CACHE
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
                        f"<b>✅ Muvaffaqiyatli!</b>\n\n"
                        f"<b>Sifat:</b> {quality}\n"
                        f"<b>Status:</b> ⚡️ Cache"
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
            "<b>⏬ Yuklanmoqda...</b>\n\n"
            f"<b>Sifat:</b> {quality}\n"
            "<b>Status:</b> Serverdan yuklanmoqda"
        )

        result = await downloader.download(url, quality)

        if not result:
            await msg.edit_text(
                "<b>❌ Yuklash muvaffaqiyatsiz</b>\n\n"
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

        await msg.edit_text("<b>📤 Yuborilmoqda...</b>")

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
                f"<b>✅ Muvaffaqiyatli!</b>\n\n"
                f"<b>Sifat:</b> {quality}\n"
                f"<b>Hajmi:</b> {file_size / 1_000_000:.1f} MB"
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
                "<b>⚠️ Kutilmagan xatolik</b>\n\n"
                "Qaytadan urinib ko'ring."
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