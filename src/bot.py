"""Bot dialogs and handlers."""

from contextlib import suppress

import structlog
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ErrorEvent
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent
from dialog_yml import DialogYAMLBuilder, FuncsRegistry

from functions import register_dialog_yml_funcs
from functions.custom import CustomCalendarModel

logger = structlog.get_logger(__name__)


async def start(_: Message, dialog_manager: DialogManager) -> None:
    """Handle /start command, resetting the dialog stack.

    Parameters
    ----------
    _ : Message
        The message object from Telegram (unused).
    dialog_manager : DialogManager
        The dialog manager instance.

    """
    # it is important to reset stack because
    # the user wants to restart everything
    user = dialog_manager.event.from_user
    logger.info("User started conversation.", user_id=user.id)
    data = dialog_manager.middleware_data
    dialog_yml: DialogYAMLBuilder = data["dialog_yml"]
    await dialog_manager.start(
        state=dialog_yml.states.Menu.MAIN,
        mode=StartMode.RESET_STACK,
    )


async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager) -> None:
    """Handle UnknownIntent error by restarting the dialog.

    Parameters
    ----------
    event : ErrorEvent
        The error event object.
    dialog_manager : DialogManager
        The dialog manager instance.

    """
    user_id = (
        dialog_manager.event.from_user.id if dialog_manager.event.from_user else "unknown"
    )
    logger.error(
        "Restarting dialog due to unknown intent.",
        user_id=user_id,
        exc_info=event.exception,
    )
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
    """Custom states group for dialogs.

    Attributes
    ----------
    state1 : State
        A generic state.
    state2 : State
        A generic state.
    state3 : State
        A generic state.

    """

    state1 = State()
    state2 = State()
    state3 = State()


def get_dialog_router() -> Router:
    """Create and configure the dialog router."""
    logger.info("Building dialogs...")
    register_dialog_yml_funcs(FuncsRegistry())
    dy_builder = DialogYAMLBuilder.build(
        yaml_file_name="main.yaml",
        yaml_dir_path="src/data",
        models={"my_calendar": CustomCalendarModel},
        states=[CustomSG],
        router=Router(name=__name__),
    )

    dy_builder.router.message.register(start, F.text == "/start")
    dy_builder.router.errors.register(
        on_unknown_intent,
        ExceptionTypeFilter(UnknownIntent),
    )
    logger.info("Dialogs built and router configured.")
    return dy_builder.router
