"""Admin Handler - Broadcast bilan"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)
router = Router()


class BroadcastStates(StatesGroup):
    waiting_message = State()


@router.message(Command('admin'))
async def cmd_admin(message: Message, config):
    if message.from_user.id not in config.bot.admin_ids:
        await message.answer("🚫 Ruxsat yo'q!")
        return

    from app.keyboards.inline import get_admin_keyboard
    await message.answer(
        "👨‍💼 <b>Admin Panel</b>\n\nTanlang:",
        reply_markup=get_admin_keyboard()
    )


@router.callback_query(F.data == 'admin_stats')
async def show_stats(callback: CallbackQuery, db, config):
    if callback.from_user.id not in config.bot.admin_ids:
        await callback.answer("🚫 Ruxsat yo'q!", show_alert=True)
        return

    try:
        stats = await db.get_stats()
        text = (
            "📊 <b>Bot Statistikasi</b>\n\n"
            f"👥 Jami: <b>{stats.get('total_users', 0):,}</b>\n"
            f"🆕 Bugun: <b>{stats.get('new_today', 0)}</b>\n"
            f"✅ Faol: <b>{stats.get('active_weekly', 0)}</b>\n\n"
            f"📥 Yuklashlar: <b>{stats.get('total_downloads', 0):,}</b>\n"
            f"📅 Bugun: <b>{stats.get('downloads_today', 0)}</b>"
        )

        from app.keyboards.inline import get_admin_keyboard
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    except Exception as e:
        logger.error(f"Stats xato: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.callback_query(F.data == 'admin_users')
async def show_users(callback: CallbackQuery, db, config):
    if callback.from_user.id not in config.bot.admin_ids:
        await callback.answer("🚫 Ruxsat yo'q!", show_alert=True)
        return

    try:
        stats = await db.get_stats()
        text = (
            "👥 <b>Foydalanuvchilar</b>\n\n"
            f"Jami: <b>{stats.get('total_users', 0):,}</b>\n"
            f"Bugun: <b>{stats.get('new_today', 0)}</b>\n"
            f"Faol: <b>{stats.get('active_weekly', 0)}</b>"
        )

        from app.keyboards.inline import get_admin_keyboard
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard())
    except Exception as e:
        logger.error(f"Users xato: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.callback_query(F.data == 'admin_broadcast')
async def start_broadcast(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.bot.admin_ids:
        await callback.answer("🚫 Ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Barcha foydalanuvchilarga yuborish uchun xabar yozing:\n\n"
        "Bekor qilish: /cancel"
    )
    await state.set_state(BroadcastStates.waiting_message)


@router.message(BroadcastStates.waiting_message)
async def process_broadcast(message: Message, state: FSMContext, db, config):
    if message.from_user.id not in config.bot.admin_ids:
        return

    if message.text == '/cancel':
        await state.clear()
        await message.answer("❌ Bekor qilindi")
        return

    try:
        # Barcha userlarni olish
        async with db.pool.acquire() as conn:
            users = await conn.fetch("SELECT user_id FROM users WHERE is_blocked = FALSE")

        total = len(users)
        success = 0
        failed = 0

        status_msg = await message.answer(f"📤 Yuborilmoqda... 0/{total}")

        for i, user in enumerate(users, 1):
            try:
                await message.bot.send_message(user['user_id'], message.text)
                success += 1

                # Har 50 tadan 1 marta status yangilash
                if i % 50 == 0:
                    await status_msg.edit_text(f"📤 Yuborilmoqda... {i}/{total}")

            except Exception:
                failed += 1

        await status_msg.edit_text(
            f"✅ <b>Broadcast tugadi!</b>\n\n"
            f"Jami: {total}\n"
            f"Yuborildi: {success}\n"
            f"Xato: {failed}"
        )

        await state.clear()

    except Exception as e:
        logger.error(f"Broadcast xato: {e}")
        await message.answer("❌ Xatolik!")
        await state.clear()


@router.message(Command('cancel'))
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi")