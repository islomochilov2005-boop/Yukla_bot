"""Konfiguratsiya - Aiogram 3.24.0"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str

    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    host: str
    port: int


@dataclass
class Config:
    bot: BotConfig
    db: DatabaseConfig
    redis: RedisConfig
    throttle_rate: float = 2.0
    max_file_size: int = 2_000_000_000


def load_config() -> Config:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN topilmadi!")

    admin_ids = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

    return Config(
        bot=BotConfig(token=token, admin_ids=admin_ids),
        db=DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            name=os.getenv('DB_NAME', 'videobot'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASS', '')
        ),
        redis=RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379))
        )
    )


config = load_config()