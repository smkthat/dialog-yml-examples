"""Callback-related functions."""

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
    """Handle notify with extra data.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query from the user.
    button : Button
        The button that triggered the callback.
    dialog_manager : DialogManager
        The dialog manager instance.
    data : Dict
        Additional data passed with the callback.

    """
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
    """Handle simple click.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query from the user.
    button : Button
        The button that triggered the callback.
    dialog_manager : DialogManager
        The dialog manager instance.
    **kwargs
        Additional keyword arguments.

    """
    if callback.message:
        await callback.message.answer("Clicked!")


async def on_click_with_data(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    data: Dict,
):
    """Handle click with data.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query from the user.
    button : Button
        The button that triggered the callback.
    dialog_manager : DialogManager
        The dialog manager instance.
    data : Dict
        Additional data passed with the callback.

    """
    if callback.message:
        await callback.message.answer(json.dumps(data, indent=4, ensure_ascii=False))


def register_notifies(registry):
    """Register callback-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.notify.register(notify_extra)
    registry.func.register(on_click_simple)
    registry.func.register(on_click_with_data)
