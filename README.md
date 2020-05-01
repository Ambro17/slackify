# Flask-Slack
![Build & Test](https://github.com/Ambro17/flask-slack/workflows/Build%20&%20Test/badge.svg)
[![codecov](https://codecov.io/gh/Ambro17/flask-slack/branch/master/graph/badge.svg)](https://codecov.io/gh/Ambro17/flask-slack)

`Flask-Slack` is a light framework designed to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

To do so, it stands on the shoulders of `Flask` and `slackclient` (_The official python slack client_) and offers a more declarative API over slack commands, events, shortcuts, actions and modals.

## Quickstart
```python
from slackify import Flack, async_task


app = Flack(__name__)


# That's it! now you can declare commands, shortcuts, actions, and whatever you please!
# No routing nightmare, no special endpoints, just declare what you want


@app.command
def hello():
    return reply_text('Hello from Slack')


# Change the slash command name to /say_bye instead of the default function name
@app.command(name='say_bye')
def bye():
    my_background_job()
    return reply_text('Bye')


@async_task
def my_background_job():
    """Non blocking long task"""
    sleep(15)
    return
```


### What about new slack Shorcuts?
See [examples/shortcuts.py](examples/shortcuts.py) for a self contained example

### But can i use new slack Modals?
Of course! See [examples/views.py](examples/views.py) for a quick example

### Are interactive actions supported?
Yes! See [examples/actions.py](examples/actions.py) for a quickstart.
>Note: Legacy actions are unsupported by design as they are discouraged by slack. Nevertheless, if there's popular demand, we could add support for them.

### And slack events?
As you may have guessed, they are also supported. See [examples/events.py](examples/events.py) for an example.


## Full example
Here you have a more complete example showcasing all functionality. It includes:
- A hello command that shows interactive buttons
- Callbacks for each interactive button click
- A register command that opens a new slack modal
- A shortcut to roll a dice and get a random number
- An event handler that echoes reactions to messages.

>Remember to `export BOT_TOKEN=xoxb-your-bot-secret` to enable slack api calls.
```python
import json
import os
import random

from slackify import (ACK, OK, Flack, async_task, block_reply, request,
                         respond, text_block, Slack)

app = Flack(__name__)
cli = Slack(os.getenv('BOT_TOKEN'))


@app.command
def hello():
    """Send hello message with question and yes no buttons"""
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
    """If a user clicks yes on the message above, execute this callback"""
    action = json.loads(request.form["payload"])
    text_blok = text_block('Super! I do too :thumbsup:')
    respond(action['response_url'], {'blocks': [text_blok]})
    return OK


@app.action("no")
def no():
    """If a user clicks no on the hello message, execute this callback"""
    action = json.loads(request.form["payload"])
    text_blok = text_block('Boo! You are so boring :thumbsdown:')
    respond(action['response_url'], {'blocks': [text_blok]})
    return OK


@app.command
def register():
    """Open a registration popup that asks for username and password. Don't enter any credentials!"""
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
    """Handle registration form submission."""
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
    """Roll a virtual dice to give a pseudo-random number"""
    payload = json.loads(request.form['payload'])
    dice_value = random.randint(1, 6)
    msg = f'🎲 {dice_value}'
    send_message(cli, blocks=[text_block(msg)], user_id=payload['user']['id'])
    return ACK


@app.event('reaction_added')
def echo_reaction(payload):
    """If any user reacts to a message, also react with that emoji to the message"""
    event = payload['event']
    reaction = event['reaction']
    cli.reactions_add(
        name=reaction,
        channel=event['item']['channel'],
        timestamp=event['item']['ts']
    )
```

## Roadmap
1. Inject payload to action/event/shortcut handlers to avoid code repetition on each handler.
2. Support for app factory pattern
3. Support for blueprints
