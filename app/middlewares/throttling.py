"""Anti-spam Middleware - Aiogram 3.24.0"""
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 2.0):
        self.rate_limit = rate_limit
        self.user_last_call: Dict[int, float] = {}

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.user_last_call:
            time_passed = current_time - self.user_last_call[user_id]

            if time_passed < self.rate_limit:
                await event.answer(f"⚠️ Iltimos {self.rate_limit:.0f} sekund kuting!")
                return

        self.user_last_call[user_id] = current_time
        return await handler(event, data)