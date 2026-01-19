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
    await callback.answer(str(selected_date))


def register_calendars(registry: FuncsRegistry):
    registry.func.register(on_date_selected)
