import os
from flask import Flask
from slackify import Slackify, Slack

# Important! Before running set FLASK_APP=examples.async_task:app
app = Flask(__name__)
slackify = Slackify(app=app)

slack = Slack(os.environ["SLACK_BOT_TOKEN"])


@slackify.event("message")
def handle_message(payload):
    """Listen to messages containing `python` and react with python emoji

    Note:
        Your event handler function *MUST* accept a positional argument with the event payload

    Preconditions:
        - Setup event subscription https://api.slack.com/events-api and point to `/slack/events` uri
        - Suscribe to `message.channels` events so your app gets notified of this event
    """
    event = payload["event"]
    if event.get("subtype") is None and 'python' in event.get('text', ''):
        slack.reactions_add(
            name='snake',
            channel=event["channel"],
            timestamp=event['ts']
        )
