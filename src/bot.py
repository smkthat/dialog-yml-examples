import logging
import os
from contextlib import suppress

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ErrorEvent

from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent
from dialog_yml import DialogYAMLBuilder, FuncsRegistry

from src.functions import register_dialog_yml_funcs
from src.functions.custom import CustomCalendarModel


async def start(_: Message, dialog_manager: DialogManager) -> None:
    # it is important to reset stack because
    # the user wants to restart everything
    data = dialog_manager.middleware_data
    dialog_yml: DialogYAMLBuilder = data["dialog_yml"]
    await dialog_manager.start(
        state=dialog_yml.states.Menu.MAIN,
        mode=StartMode.RESET_STACK,
    )


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager) -> None:
    """Example of handling UnknownIntent Error and starting new dialog."""
    logging.error("Restarting dialog: %s", event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            "Bot process was restarted due to maintenance.\nRedirecting to main menu.",
        )
        message = event.update.callback_query.message
        if isinstance(message, Message):
            try:
                await message.delete()
            except TelegramBadRequest:
                with suppress(TelegramBadRequest):
                    await message.edit_caption(caption=" ", reply_markup=None)
                with suppress(TelegramBadRequest):
                    await message.edit_text(text=" ", reply_markup=None)
    data = dialog_manager.middleware_data
    dialog_yml: DialogYAMLBuilder = data["dialog_yml"]
    await dialog_manager.start(
        state=dialog_yml.states.Menu.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


class CustomSG(StatesGroup):
    state1 = State()
    state2 = State()
    state3 = State()


async def main() -> None:
    load_dotenv()
    logging.basicConfig(
        level=getattr(
            logging,
            os.getenv("MEGA_BOT_LOG_LEVEL", "INFO").upper(),
            logging.INFO,
        ),
        format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
    )

    register_dialog_yml_funcs(FuncsRegistry())
    dy_builder = DialogYAMLBuilder.build(
        yaml_file_name="main.yaml",
        yaml_dir_path="src/data",
        models={"my_calendar": CustomCalendarModel},
        states=[CustomSG],
        router=Router(),
    )

    dy_builder.router.message.register(start, F.text == "/start")
    dy_builder.router.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(dy_builder.router)
    bot = Bot(token=os.getenv("MEGA_BOT_TOKEN", ""))
    await bot.get_updates(offset=-1)
    await dp.start_polling(bot)
