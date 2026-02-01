"""Application entry point and initialization."""

import asyncio
import os

import structlog
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage, RedisEventIsolation
from redis.asyncio import Redis

from src.bot import get_dialog_router
from src.logs import setup_logger

logger = structlog.get_logger(__name__)


async def on_startup(bot: Bot):
    """Handle bot startup."""
    logger.info("Executing startup tasks...")
    await bot.get_updates(offset=-1)  # Drop pending updates
    logger.info("Bot startup complete.")


async def on_shutdown(dispatcher: Dispatcher):
    """Handle bot shutdown."""
    logger.info("Executing shutdown tasks...")
    await dispatcher.storage.close()
    logger.info("Bot shutdown complete.")


async def main() -> None:
    """Initialize and start the bot."""
    load_dotenv()
    setup_logger()

    bot = Bot(token=os.getenv("MEGA_BOT_TOKEN", ""))

    logger.debug("Creating Redis client...")
    redis_client = Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB", 0)),
    )
    logger.info(
        "Redis client created.",
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", 6379)),
    )

    key_builder = DefaultKeyBuilder(
        prefix="spoetka_base:fsm",
        with_destiny=True,
    )

    logger.debug("Creating FSM storage...")
    storage = RedisStorage(
        redis=redis_client,
        key_builder=key_builder,
    )
    logger.info("FSM storage created.", type=type(storage).__name__)

    logger.debug("Creating Dispatcher...")
    dp = Dispatcher(
        storage=storage,
        events_isolation=RedisEventIsolation(
            redis=redis_client,
            key_builder=key_builder,
        ),
    )
    logger.info("Dispatcher created.")

    # Register startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Include the main dialog router
    logger.debug("Including dialog router...")
    dp.include_router(get_dialog_router())
    logger.info("Dialog router included.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
