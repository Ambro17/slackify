from slackeventsapi import SlackEventAdapter
import os
from flask_slack import Flack, Slack


app = Flack(__name__)

events = SlackEventAdapter(os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app)
slack_client = Slack(os.environ["SLACK_BOT_TOKEN"])


@events.on("message")
def handle_message(event_data):
    """Listen to message events and react with python emoji

    Preconditions:
        - Setup event subscription https://api.slack.com/events-api
        - Suscribe to `message.channels` events so your app gets notified
    """
    event = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if event.get("subtype") is None and 'python' in event.get('text', ''):
        channel = event["channel"]
        timestamp = event['ts']
        slack_client.reactions_add(name='snake', channel=channel, timestamp=timestamp)


@events.on("message")
def handle_message2(event_data):
    """Listen to message events and react with python emoji

    Preconditions:
        - Setup event subscription https://api.slack.com/events-api
        - Suscribe to `message.channels` events so your app gets notified
    """
    event = event_data["event"]
    # If the incoming message contains "hi", then respond with a "Hello" message
    if event.get("subtype") is None and 'python' in event.get('text', ''):
        channel = event["channel"]
        timestamp = event['ts']
        slack_client.reactions_add(name='thumbsup', channel=channel, timestamp=timestamp)