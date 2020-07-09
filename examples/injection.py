from flask import Flask
from slackify import Slackify, reply_text
from slackify.slack import block_reply, text_block

app = Flask(__name__)
slackify = Slackify(app=app)


@slackify.command
def hello(command, command_args, response_url):
    return reply_text(f"You called `{command} {command_args}`. POST to {response_url} for delayed responses (>3sec)")


@slackify.shortcut('greet_me')
def goodbye(shortcut):
    reply_block = [text_block(f"Shortcut payload was\n```{shortcut}```")]
    return block_reply(reply_block)


@slackify.action('some_action')
def action(payload):
    reply_block = [text_block(f"Shortcut payload was\n```{payload}```")]
    return block_reply(reply_block)
