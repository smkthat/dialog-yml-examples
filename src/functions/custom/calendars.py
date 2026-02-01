"""Custom calendar widgets and models."""

from datetime import date

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarScopeView,
    CalendarDaysView,
    CalendarMonthView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Text, Format
from babel.dates import get_day_names, get_month_names

from dialog_yml.models.widgets.calendars import CalendarModel
from dialog_yml.utils import clean_empty


class WeekDay(Text):
    """Renders weekday names."""

    async def _render_text(self, data, manager: DialogManager) -> str:
        """Render weekday name based on locale.

        Parameters
        ----------
        data : dict
            The data for rendering, including 'date'.
        manager : DialogManager
            The dialog manager instance.

        Returns
        -------
        str
            The localized weekday name.

        """
        selected_date: date = data["date"]
        user = manager.event.from_user
        locale = user.language_code if user and user.language_code else "en"
        return get_day_names(
            width="short",
            context="stand-alone",
            locale=locale,
        )[selected_date.weekday()].title()


class Month(Text):
    """Renders month names."""

    async def _render_text(self, data, manager: DialogManager) -> str:
        """Render month name based on locale.

        Parameters
        ----------
        data : dict
            The data for rendering, including 'date'.
        manager : DialogManager
            The dialog manager instance.

        Returns
        -------
        str
            The localized month name.

        """
        selected_date: date = data["date"]
        user = manager.event.from_user
        locale = user.language_code if user and user.language_code else "en"
        return get_month_names(
            "wide",
            context="stand-alone",
            locale=locale,
        )[selected_date.month].title()


class Year(Text):
    """Renders year."""

    async def _render_text(self, data, manager: DialogManager) -> str:
        """Render year string.

        Parameters
        ----------
        data : dict
            The data for rendering, including 'date'.
        manager : DialogManager
            The dialog manager instance.

        Returns
        -------
        str
            The year as a string.

        """
        selected_date: date = data["date"]
        return str(selected_date.year)


class CustomCalendar(Calendar):
    """Custom calendar widget with localized text."""

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        """Initialize calendar views with custom texts.

        Returns
        -------
        dict[CalendarScope, CalendarScopeView]
            A dictionary mapping calendar scopes to their respective views.

        """
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " 👉🏽",
                prev_month_text="👈🏽 " + Month(),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text=Format("{date:%Y}"),
                this_month_text="[" + Month() + "]",
                next_year_text=Year() + " 👉🏽",
                prev_year_text="👈🏽 " + Year(),
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
                year_text=Year(),
                next_page_text=Year() + " 👉🏽",
                prev_page_text="👈🏽 " + Year(),
                this_year_text="[" + Year() + "]",
            ),
        }


class CustomCalendarModel(CalendarModel):
    """Model for the custom calendar widget."""

    def to_object(self) -> CustomCalendar:
        """Create a CustomCalendar object from the model.

        Returns
        -------
        CustomCalendar
            An instance of the custom calendar.

        """
        kwargs = clean_empty(
            {
                "id": self.id,
                "on_click": self.on_click.func if self.on_click else None,
                "when": self.when.func if self.when else None,
            }
        )
        return CustomCalendar(**kwargs)
