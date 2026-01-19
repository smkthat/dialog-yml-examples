from dialog_yml import FuncsRegistry


def get_fruit_item(x):
    return x


def register_layouts(registry: FuncsRegistry):
    registry.func.register(get_fruit_item)
