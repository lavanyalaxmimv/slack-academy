from . import actions, commands, discount, shortcuts


def register_listeners(app):
    commands.register(app)
    actions.register(app)
    shortcuts.register(app)
    discount.register(app)