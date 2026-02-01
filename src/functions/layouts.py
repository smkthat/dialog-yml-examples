"""Layout-related functions."""

from dialog_yml import FuncsRegistry


def get_fruit_item(x):
    """Get fruit item.

    Parameters
    ----------
    x : Any
        The item to return.

    Returns
    -------
    Any
        The input item.

    """
    return x


def register_layouts(registry: FuncsRegistry):
    """Register layout-related functions.

    Parameters
    ----------
    registry : FuncsRegistry
        The registry to register functions with.

    """
    registry.func.register(get_fruit_item)
