"""Calendar-related functions."""

from datetime import date

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedCalendar

from dialog_yml import FuncsRegistry


async def on_date_selected(
    callback: CallbackQuery,
    widget: ManagedCalendar,
    manager: DialogManager,
    selected_date: date,
):
    """Handle date selection from calendar.

    Parameters
    ----------
    callback : CallbackQuery
        The callback query from the user.
    widget : ManagedCalendar
        The managed calendar widget.
    manager : DialogManager
        The dialog manager instance.
    selected_date : date
        The date selected by the user.

    """
    await callback.answer(str(selected_date))


def register_calendars(registry: FuncsRegistry):
    """Register calendar-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(on_date_selected)
