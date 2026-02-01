"""Counter-related functions."""

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedCounter

from dialog_yml import FuncsRegistry


async def counter_getter(dialog_manager: DialogManager, **kwargs):
    """Get progress for the counter.

    Parameters
    ----------
    dialog_manager : DialogManager
        The dialog manager instance.
    **kwargs
        Additional keyword arguments.

    Returns
    -------
    dict
        A dictionary containing the current progress.

    """
    progress = 0
    if counter := dialog_manager.find("counter"):
        progress = counter.get_value() / 10 * 100
    return {"progress": progress}


async def on_text_click(
    event: CallbackQuery,
    widget: ManagedCounter,
    manager: DialogManager,
) -> None:
    """Handle text click on counter.

    Parameters
    ----------
    event : CallbackQuery
        The callback query event.
    widget : ManagedCounter
        The managed counter widget.
    manager : DialogManager
        The dialog manager instance.

    """
    await event.answer(f"Value: {widget.get_value()}")


def register_counters(registry: FuncsRegistry):
    """Register counter-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(counter_getter)
    registry.func.register(on_text_click)
