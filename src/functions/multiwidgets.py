"""Multiwidget-related functions."""

from dialog_yml import FuncsRegistry


def item_id_getter(x, *args, **kwargs):
    """Get item ID.

    Parameters
    ----------
    x : Any
        The item.
    *args
        Variable length argument list.
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    Any
        The input item `x`.

    """
    return x


def register_multiwidgets(registry: FuncsRegistry):
    """Register multiwidgets functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(item_id_getter)
