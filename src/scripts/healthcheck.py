"""Health check script for the bot."""

import os
import asyncio
import sys

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramUnauthorizedError
import structlog


logger = structlog.get_logger(__name__)


async def check_bot_connection():
    """Checks the bot's connection to the Telegram API.

    This function attempts to retrieve information about the bot using `bot.get_me()`.
    If successful, it indicates a healthy connection. Otherwise, it logs an error
    and exits with a non-zero status code.

    Raises
    ------
    SystemExit
        Exits with 0 if connection is successful, 1 otherwise.

    """

    bot = Bot(token=os.getenv("MEGA_BOT_TOKEN", ""))
    try:
        await bot.get_me()
        # If get_me() is successful, it means the token is valid and connection is up.
        logger.info("Healthcheck successful: connection to Telegram API is OK.")
        sys.exit(0)
    except TelegramUnauthorizedError:
        logger.error("Healthcheck failed: Bot token is invalid.")
        sys.exit(1)
    except TelegramAPIError as e:
        logger.error("Healthcheck failed: Telegram API error: %s", e)
        sys.exit(1)
    except Exception as e:
        # This catches other potential issues like network problems.
        logger.error("Healthcheck failed: An unexpected error occurred: %s", e)
        sys.exit(1)
    finally:
        # It's important to close the bot session.
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(check_bot_connection())
