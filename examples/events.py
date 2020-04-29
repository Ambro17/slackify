import os
from flask_slack import Flack, Slack

app = Flack(__name__)

slack = Slack(os.environ["SLACK_BOT_TOKEN"])


@app.event("message")
def handle_message(payload):
    """Listen to message events and react with python emoji

    Note:
        *ALL* event handlers will receive a payload positional argument with the event info.

    Preconditions:
        - Setup event subscription https://api.slack.com/events-api
        - Suscribe to `message.channels` events so your app gets notified
    """
    event = payload["event"]
    if event.get("subtype") is None and 'python' in event.get('text', ''):
        slack.reactions_add(
            name='snake',
            channel=event["channel"],
            timestamp=event['ts']
        )
