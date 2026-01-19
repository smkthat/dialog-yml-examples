from typing import Any

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput


async def data_getter(dialog_manager: DialogManager, *_args, **_kwargs) -> dict[str, Any]:
    chk_widget = dialog_manager.find("chk")
    emoji_widget = dialog_manager.find("emoji")

    return {
        "name": dialog_manager.dialog_data.get("name", ""),
        "option": chk_widget.is_checked() if chk_widget else False,
        "emoji": emoji_widget.get_checked() if emoji_widget else False,
    }


async def set_name(message: Message, message_input: MessageInput, manager: DialogManager):
    manager.dialog_data["name"] = message.text
    await manager.next()


def register_switch(registry):
    registry.func.register(data_getter)
    registry.func.register(set_name)
