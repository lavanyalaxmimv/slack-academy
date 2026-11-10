from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners
from services import config

app = App(token=config.SLACK_BOT_TOKEN)
register_listeners(app)

if __name__ == "__main__":
    SocketModeHandler(app, config.SLACK_APP_TOKEN).start()