"""Selection-related functions."""

from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from dialog_yml import FuncsRegistry


@dataclass
class Fruit:
    """Represents a fruit with an ID and a name.

    Attributes
    ----------
    id : str
        The unique identifier of the fruit.
    name : str
        The name of the fruit.

    """

    id: str
    name: str


async def getter(*args, **_kwargs):
    """Get a list of fruits.

    Parameters
    ----------
    *args
        Variable length argument list (unused).
    **_kwargs
        Arbitrary keyword arguments (unused).

    Returns
    -------
    dict
        A dictionary containing a list of Fruit objects.

    """
    return {
        "fruits": [
            Fruit("1", "Apple"),
            Fruit("2", "Banana"),
            Fruit("3", "Orange"),
            Fruit("4", "Pear"),
        ]
    }


def fruit_id_getter(fruit: Fruit) -> str:
    """Get the ID of a fruit.

    Parameters
    ----------
    fruit : Fruit
        The Fruit object.

    Returns
    -------
    str
        The ID of the fruit.

    """
    return fruit.id


async def on_item_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
):
    """Handle selection of an item.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query from the user.
    widget : Any
        The widget that triggered the selection.
    manager : DialogManager
        The dialog manager instance.
    selected_item : str
        The ID of the selected item.

    """
    await callback.answer(f"item id: {selected_item}")


def register_selects(registry: FuncsRegistry):
    """Register select-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(getter)
    registry.func.register(fruit_id_getter)
    registry.func.register(on_item_selected)
