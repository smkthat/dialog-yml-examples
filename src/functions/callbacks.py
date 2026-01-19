import json
from typing import Dict

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button


async def notify_extra(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: Dict,
) -> None:
    if extra_data := data.pop("extra_data", {}):
        text = data["text"]
        data["text"] = f"{text}\n\n{extra_data}"

    await callback.answer(**data)


async def on_click_simple(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
):
    if callback.message:
        await callback.message.answer("Clicked!")


async def on_click_with_data(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: Dict,
):
    if callback.message:
        await callback.message.answer(json.dumps(data, indent=4, ensure_ascii=False))


def register_notifies(registry):
    registry.notify.register(notify_extra)
    registry.func.register(on_click_simple)
    registry.func.register(on_click_with_data)
