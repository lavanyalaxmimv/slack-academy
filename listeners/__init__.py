from . import actions, commands, discount, functions, home, orderflow, shortcuts,accounts


def register_listeners(app):
    commands.register(app)
    actions.register(app)
    shortcuts.register(app)
    discount.register(app)
    home.register(app)
    orderflow.register(app)
    functions.register(app)
    accounts.register(app)