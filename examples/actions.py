from flask import Flask
from slackify import Slackify, respond, Slack, reply, request, OK
import json

app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack('xoxb-SECRET-token')


def text_block(text):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }


@slackify.command
def askme():
    """Slack API recommended way of making messages interactive is through blocks

    Messages no longer are simple text. Even if you want to send just text, the
    recommended way is to create a section block, with the text property.
    """

    # This is simple text, wrapped in a section to comply with slack new recommendations
    message_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Do you like bots?"
        }
    }

    # And here it gets cool. Actions blocks are what make messages special.
    # Here we include two button elements. But there are many more elements.
    # Check them out at https://api.slack.com/reference/block-kit/block-elements
    buttons_block = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "Yes"
                },
                "style": "primary",
                "value": "i_like_bots",
                "action_id": "yes"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "No"
                },
                "style": "danger",
                "value": "i_dont_like_bots",
                "action_id": "no"
            }
        ]
    }
    blocks = [
        message_block,
        buttons_block
    ]
    message_as_blocks = {
        'blocks': blocks
    }
    return reply(message_as_blocks)


@slackify.action("yes")
def yes():
    """You may ask here, why do we respond to response_url instead of the request itself?

    Well, slack decided you can't respond directly to interaction actions requests.
    So we must use the response_url. If you know why did they decide this please tell
    me. I'm sure they might be a reason but it isn't obvious to me..
    """
    action = json.loads(request.form["payload"])

    text_blok = text_block('Super! I do too :thumbsup:')
    blocks = {'blocks': [text_blok]}
    respond(action['response_url'], blocks)
    return OK


@slackify.action("no")
def no():
    action = json.loads(request.form["payload"])

    text_blok = text_block('Boo! You are so boring :thumbsdown:')
    blocks = {'blocks': [text_blok]}
    respond(action['response_url'], blocks)
    return OK
