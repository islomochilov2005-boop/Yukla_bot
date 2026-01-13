"""Logging middleware"""
import logging
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Barcha xabarlarni loglash
    """

    async def on_pre_process_message(self, message: types.Message, data: dict):
        """Xabar kelganda"""
        user = message.from_user

        log_message = (
            f"📨 Message | "
            f"User: {user.id} (@{user.username or 'no_username'}) | "
            f"Text: {message.text[:50] if message.text else '[no text]'}..."
        )

        logger.info(log_message)

    async def on_pre_process_callback_query(self, callback: types.CallbackQuery, data: dict):
        """Callback kelganda"""
        user = callback.from_user

        log_message = (
            f"🔘 Callback | "
            f"User: {user.id} (@{user.username or 'no_username'}) | "
            f"Data: {callback.data}"
        )

        logger.info(log_message)

    async def on_post_process_message(self, message: types.Message, results, data: dict):
        """Xabar qayta ishlangandan keyin"""
        pass

    async def on_post_process_callback_query(self, callback: types.CallbackQuery, results, data: dict):
        """Callback qayta ishlangandan keyin"""
        pass