from . import actions, commands, shortcuts


def register_listeners(app):
    commands.register(app)
    actions.register(app)
    shortcuts.register(app)