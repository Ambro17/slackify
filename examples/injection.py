from flask import Flask
from slackify import Slackify, reply_text, Slack, ACK

app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack('xoxb-SECRET')

@slackify.command
def hello(command, command_args, response_url):
    return reply_text(f"You called `{command} {command_args}`. POST to {response_url} for delayed responses (>3sec)")


@slackify.shortcut('greet_me')
def goodbye(payload):
    cli.chat_postMessage(channel='#general', text=f'Knock Knock\n`{payload}`')
    return ACK
