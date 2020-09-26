<p align="center">
    <img src="https://raw.githubusercontent.com/Ambro17/slackify/master/docs/logopro.svg" title="Logo">
</p>
<p align="center">
    <img alt="Build" src="https://github.com/Ambro17/flask-slack/workflows/Build%20&%20Test/badge.svg">
    <a href="https://codecov.io/gh/Ambro17/slackify">
        <img alt="Codecov" src="https://codecov.io/gh/Ambro17/flask-slack/branch/master/graph/badge.svg">
    </a>
    <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white">
</p>

# Slackify
`Slackify` is a lightweight framework that lets you quickly develop modern Slack bots focusing in **what you want** instead of struggling with *how to do it*

## Installation
`python3 -m pip install slackify`

_Requires python3.6+_

## Documentation
You can read `Slackify` docs [here](https://ambro17.github.io/slackify/)

## Quickstart
**1. 1-Click Deploy**

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Ambro17/slackify/tree/master)

> The server will listen at `<heroku_url>/` for commands/actions and `<heroku_url>/slack/events` for slack events

> This setup uses flask builtin server which is NOT suited for production. Replace it by gunicorn or similar when ready to ship


**2. Manual deploy**

Create a file named `quickstart.py` with the following content and then run `python quickstart.py`
```python
from time import sleep
from flask import Flask
from slackify import (
    Slackify,
    async_task,
    reply_text
)

app = Flask(__name__)
slackify = Slackify(app=app)


@slackify.command
def hello():
    my_background_job()
    return reply_text('Hello from Slack!')


@async_task
def my_background_job():
    """My long background job"""
    sleep(15)
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Now the server is already running, but we need to make it reachable by slack.
To do so follow these steps:

0. [Create a slack app](https://api.slack.com/apps?new_app=1)
1. Download [ngrok*](https://ngrok.com/download) and run `ngrok http 5000` to create a https proxy to localhost
2. [Create a slash command](https://api.slack.com/apps) and set the url to ngrok's https url of step `#1`
3. Write `/hello` to your new slack bot and let the magic begin ✨

>*This is a development setup so you can quickly see your code changes in slack without the need to redeploy your whole site.
> Once your bot is ready for production you should update your commands url to a permanent one.
> [Heroku](https://duckduckgo.com/?q=flask+on+heroku&t=brave&ia=web) might be a good choice if you are just getting started as it has a generous free tier.

### Features

- **Slash Commands**. [Quickstart](https://github.com/Ambro17/slackify/blob/master/examples/commands.py)
- **Global and Message Shortcuts**. [Quickstart](https://github.com/Ambro17/slackify/blob/master/examples/shortcuts.py)
- **Interactive Actions**. [Quickstart](https://github.com/Ambro17/slackify/blob/master/examples/actions.py)
- **Modals (a.k.a views)**. [Quickstart](https://github.com/Ambro17/slackify/blob/master/examples/views.py)
- **Event Hooks**. [Quickstart](https://github.com/Ambro17/slackify/blob/master/examples/events.py)

## Full example
If you want a full stack example showcasing all functionality. It includes:
- A hello command that shows interactive buttons
- Callbacks for each interactive button click
- A register command that opens a new slack modal
- A callback on modal form submission
- A shortcut to roll a dice and get a random number
- An event handler that echoes reactions to messages.
- A greeting whenever someone says `hello` in a channel where the bot is present.
>Remember to `export BOT_TOKEN=xoxb-your-bot-secret` to enable slack api calls.


```python
import json
import os
import random

from flask import Flask
from slackify import (
    ACK, OK, Slackify, async_task, block_reply,
    request, respond, text_block, Slack
)

app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack(os.getenv('BOT_TOKEN'))


@slackify.command
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


@slackify.action("yes")
def yes(payload):
    """Run this if a user clicks yes on the message above"""
    text_blok = text_block('Super! I do too :thumbsup:')
    respond(payload['response_url'], {'blocks': [text_blok]})
    return OK


@slackify.action("no")
def no(payload):
    """Run this if a user clicks no on the message above"""
    text_blok = text_block('Boo! You are so boring :thumbsdown:')
    respond(payload['response_url'], {'blocks': [text_blok]})
    return OK


@slackify.command
def register():
    """Open a registration popup that asks for username and password."""
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


@slackify.view("registration_form")
def register_callback(payload):
    """Handle registration form submission."""
    response = payload['view']['state']['values']
    text_blok = text_block(
        ':heavy_check_mark: You are now registered.\n
        f'Form payload:\n```{response}```'
    )
    send_message(cli, [text_blok], payload['user']['id'])
    return ACK


@async_task
def send_message(cli, blocks, user_id):
    return cli.chat_postMessage(channel=user_id, user_id=user_id, blocks=blocks)


@slackify.shortcut('dice_roll')
def dice_roll(payload):
    """Roll a virtual dice to give a pseudo-random number"""
    dice_value = random.randint(1, 6)
    msg = f'🎲 {dice_value}'
    send_message(
        cli,
        blocks=[text_block(msg)],
        user_id=payload['user']['id']
    )
    return ACK


@slackify.event('reaction_added')
def echo_reaction(payload):
    """Adds the same reaction as the user"""
    event = payload['event']
    reaction = event['reaction']
    cli.reactions_add(
        name=reaction,
        channel=event['item']['channel'],
        timestamp=event['item']['ts']
    )


@slackify.message('hello')
def say_hi(payload):
    event = payload['event']
    cli.chat_postMessage(
        channel=event['channel'],
        text='Hi! 👋'
    )
```


## Dependency Injection
As you add more and more commands you will find yourself parsing slack's request over and over again.

Slackify offers shortcut for this using dependency injection.
```python
@slackify.command
def hello(command, command_args, response_url):
    return reply_text(
        f"You called `{command} {command_args}`. Use {response_url} for delayed responses"
    )
```

Your view function will now receive the slash command, the arguments and the response_url upon invocation. Pretty cool, right?

If you are a user of pytest, this idea is similar to pytest fixtures

See [examples/injection.py](examples/injection.py) for the full example


## Blueprint Support
If you already have a Flask app, you can attach
flask functionality _slackifying_ your blueprint
```python
# slack_blueprint.py
from slackify import Slackify, reply_text, Blueprint

bp = Blueprint('slackify_bp', __name__, url_prefix='/slack')
slackify = Slackify(app=bp)


@slackify.command
def hello():
    return reply_text('Hello from a blueprint')


# app.py
from flask import Flask
from slack_blueprint import bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

```
> Note: You must import Blueprint from slackify instead of flask to get it working

## Dependencies
This projects uses `Flask` as the web server and `slackclient` (_The official python slack client_) as slack's API wrapper. It also uses `pyee` for async handling of events
