"""Scrolling-related functions."""

import calendar

from aiogram_dialog import DialogManager

from dialog_yml import FuncsRegistry


async def product_getter(**_kwargs):
    """Get a list of products.

    Returns
    -------
    dict
        A dictionary containing a list of products.

    """
    return {
        "products": [(f"Product {i}", i) for i in range(1, 30)],
    }


async def paging_getter(dialog_manager: DialogManager, **_kwargs):
    """Get paging information for a scroll widget.

    Parameters
    ----------
    dialog_manager : DialogManager
        The dialog manager instance.
    **_kwargs
        Arbitrary keyword arguments (unused).

    Returns
    -------
    dict
        A dictionary containing paging information.

    """
    scroll_widget = dialog_manager.find("stub_scroll")
    if scroll_widget is None:
        current_page = 0
    else:
        current_page = await scroll_widget.get_page()
    return {
        "pages": 7,
        "current_page": current_page + 1,
        "day": calendar.day_name[current_page % 7],  # Ensure index is within bounds
    }


def register_scrolls(registry: FuncsRegistry):
    """Register scroll-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(product_getter)
    registry.func.register(paging_getter)
