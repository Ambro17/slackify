import re
import os
from slackify import Flack, Slack, reply_text


app = Flack(__name__)
slack = Slack(os.getenv('BOT_TOKEN'))


@app.message('hello')
def say_hi(payload):
    event = payload['event']
    slack.chat_postMessage(channel=event['channel'], text='Hi! 👋')


BYE_REGEX = re.compile(r'bye|goodbye|see you|chau')
@app.message(BYE_REGEX)
def say_bye(payload):
    event = payload['event']
    slack.chat_postMessage(
        channel=event['channel'],
        text=f"See you tomorrow <@{event['user']}> 👋"
    )
