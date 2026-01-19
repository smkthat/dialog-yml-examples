from dialog_yml import FuncsRegistry


def item_id_getter(x, *args, **kwargs):
    return x


def register_multiwidgets(registry: FuncsRegistry):
    registry.func.register(item_id_getter)
