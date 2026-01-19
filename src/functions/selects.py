from dataclasses import dataclass
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from dialog_yml import FuncsRegistry


@dataclass
class Fruit:
    id: str
    name: str


async def getter(*args, **_kwargs):
    return {
        "fruits": [
            Fruit("1", "Apple"),
            Fruit("2", "Banana"),
            Fruit("3", "Orange"),
            Fruit("4", "Pear"),
        ]
    }


def fruit_id_getter(fruit: Fruit) -> str:
    return fruit.id


async def on_item_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
):
    await callback.answer(f"item id: {selected_item}")


def register_selects(registry: FuncsRegistry):
    registry.func.register(getter)
    registry.func.register(fruit_id_getter)
    registry.func.register(on_item_selected)
