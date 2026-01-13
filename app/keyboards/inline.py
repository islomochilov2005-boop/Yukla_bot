"""Klaviaturalar - Aiogram 3.24.0"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_quality_keyboard(url_id: int) -> InlineKeyboardMarkup:
    """Sifat tanlash - QISQA callback_data!"""
    buttons = [
        [InlineKeyboardButton(text="📹 360p", callback_data=f"dl:{url_id}:360p")],
        [InlineKeyboardButton(text="📹 480p", callback_data=f"dl:{url_id}:480p")],
        [InlineKeyboardButton(text="📹 720p", callback_data=f"dl:{url_id}:720p")],
        [InlineKeyboardButton(text="📹 1080p", callback_data=f"dl:{url_id}:1080p")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Users", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="❌ Yopish", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)