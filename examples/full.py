import json
import os
import random

from flask_slack import (ACK, OK, Flack, async_task, block_reply, request,
                         respond, text_block, Slack)

app = Flack(__name__)
cli = Slack(os.getenv('BOT_TOKEN'))


@app.command
def hello():
    YES = 'yes'
    NO = 'no'
    yes_no_buttons_block = {
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
                "action_id": YES
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
                "action_id": NO
            }
        ]
    }
    blocks = [
        text_block('Do you like Bots?'),
        yes_no_buttons_block
    ]
    return block_reply(blocks)


@app.action("yes")
def yes():
    action = json.loads(request.form["payload"])
    text_blok = text_block('Super! I do too :thumbsup:')
    respond(action['response_url'], {'blocks': [text_blok]})
    return OK


@app.action("no")
def no():
    action = json.loads(request.form["payload"])
    text_blok = text_block('Boo! You are so boring :thumbsdown:')
    respond(action['response_url'], {'blocks': [text_blok]})
    return OK


@app.command
def register():
    username_input_block = {
        "type": "input",
        "block_id": "username_block",
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter your username"
            },
            "action_id": "username_value"
        },
        "label": {
            "type": "plain_text",
            "text": "👤 Username",
            "emoji": True
        }
    }
    password_input_block = {
        "type": "input",
        "block_id": "password_block",
        "element": {
            "type": "plain_text_input",
            "placeholder": {
                "type": "plain_text",
                "text": "Enter your password"
            },
            "action_id": "password_value"
        },
        "label": {
            "type": "plain_text",
            "text": "🔑 Password",
            "emoji": True
        }
    }
    modal_blocks = [
        username_input_block,
        password_input_block,
    ]
    callback_id = 'registration_form'
    registration_form = {
        "type": "modal",
        "callback_id": callback_id,
        "title": {
            "type": "plain_text",
            "text": "My First Modal",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Register",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": modal_blocks
    }
    cli.views_open(
        trigger_id=request.form['trigger_id'],
        view=registration_form
    )
    return OK


@app.view("registration_form")
def register_callback():
    action = json.loads(request.form["payload"])
    response = action['view']['state']['values']
    text_blok = text_block(f':heavy_check_mark: You are now registered.\nForm payload:\n```{response}```')
    send_message(cli, [text_blok], action['user']['id'])
    return ACK


@async_task
def send_message(cli, blocks, user_id):
    return cli.chat_postMessage(channel=user_id, user_id=user_id, blocks=blocks)


@app.shortcut('dice_roll')
def dice_roll():
    payload = json.loads(request.form['payload'])
    dice_value = random.randint(1, 6)
    msg = f'🎲 {dice_value}'
    send_message(cli, blocks=[text_block(msg)], user_id=payload['user']['id'])
    return ACK


@app.event('reaction_added')
def echo_reaction(payload):
    event = payload['event']
    reaction = event['reaction']
    cli.reactions_add(
        name=reaction,
        channel=event['item']['channel'],
        timestamp=event['item']['ts']
    )
