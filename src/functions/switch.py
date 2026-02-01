"""Switch-related functions."""

from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput


async def data_getter(dialog_manager: DialogManager, *_args, **_kwargs) -> dict[str, Any]:
    """Get data for the switch dialog.

    Parameters
    ----------
    dialog_manager : DialogManager
        The dialog manager instance.
    *_args
        Variable length argument list (unused).
    **_kwargs
        Arbitrary keyword arguments (unused).

    Returns
    -------
    dict[str, Any]
        A dictionary containing the current state data for the switch dialog.

    """
    chk_widget = dialog_manager.find("chk")
    emoji_widget = dialog_manager.find("emoji")

    return {
        "name": dialog_manager.dialog_data.get("name", ""),
        "option": chk_widget.is_checked() if chk_widget else False,
        "emoji": emoji_widget.get_checked() if emoji_widget else False,
    }


async def set_name(message: Message, message_input: MessageInput, manager: DialogManager):
    """Set the user's name in the dialog data.

    Parameters
    ----------
    message : Message
        The message object from Telegram.
    message_input : MessageInput
        The message input widget.
    manager : DialogManager
        The dialog manager instance.

    """
    manager.dialog_data["name"] = message.text
    await manager.next()


def register_switch(registry):
    """Register switch-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(data_getter)
    registry.func.register(set_name)
