from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedCounter

from dialog_yml import FuncsRegistry


async def counter_getter(dialog_manager: DialogManager, **kwargs):
    progress = 0
    if counter := dialog_manager.find("counter"):
        progress = counter.get_value() / 10 * 100
    return {"progress": progress}


async def on_text_click(
    event: CallbackQuery,
    widget: ManagedCounter,
    manager: DialogManager,
) -> None:
    await event.answer(f"Value: {widget.get_value()}")


def register_counters(registry: FuncsRegistry):
    registry.func.register(counter_getter)
    registry.func.register(on_text_click)
