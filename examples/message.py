import re
import os
from flask import Flask
from slackify import Slackify, Slack


# Important! Before running set FLASK_APP=examples.async_task:app
app = Flask(__name__)
slackify = Slackify(app=app)
slack = Slack(os.getenv('BOT_TOKEN'))


@slackify.message('hello')
def say_hi(payload):
    event = payload['event']
    slack.chat_postMessage(channel=event['channel'], text='Hi! 👋')


BYE_REGEX = re.compile(r'bye|goodbye|see you|chau')
@slackify.message(BYE_REGEX)
def say_bye(payload):
    event = payload['event']
    slack.chat_postMessage(
        channel=event['channel'],
        text=f"See you tomorrow <@{event['user']}> 👋"
    )
