# Slackify
![Build & Test](https://github.com/Ambro17/flask-slack/workflows/Build%20&%20Test/badge.svg)
[![codecov](https://codecov.io/gh/Ambro17/flask-slack/branch/master/graph/badge.svg)](https://codecov.io/gh/Ambro17/flask-slack)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

`Slackify` is a light framework designed to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

To do so, it stands on the shoulders of `Flask` and `slackclient` (_The official python slack client_) and offers a more declarative API over slack commands, events, shortcuts, actions and modals.

## Installation
`python3 -m pip install slackify`

_Requires python3.6+_

## Quickstart
**1. The easy way:**

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Ambro17/slackify/tree/master)

> The server will listen at `<heroku_url>/` for commands/actions and `<heroku_url>/slack/events` for slack events

> This setup uses flask builtin server which is NOT suited for production. Replace it by gunicorn or similar when ready to ship


**2. The manual way**

Create a file named `quickstart.py` with the following content
```python
from flask import Flask
from slackify import Slackify, async_task


app = Flask(__name__)
slackify = Slackify(app=app)


@slackify.command
def hello():
    return reply_text('Hello from Slack')


# Change the slash command name to /say_bye instead of the default function name
@slackify.command(name='say_bye')
def bye():
    my_background_job()
    return reply_text('Bye')


@async_task
def my_background_job():
    """Non blocking long task"""
    sleep(15)
    return
```

To connect it to slack you need to meet this preconditions:

0. [Create a slack app](https://api.slack.com/apps?new_app=1)
1. Download [ngrok*](https://ngrok.com/download) and run `ngrok http 5000` to create a https proxy to localhost
2. [Create a slash command](https://api.slack.com/apps) and set the url to ngrok's https url of step #1
3. On your terminal export flask app variable `export FLASK_APP='quickstart:app'`
4. Run your app with `flask run --port=5000` (The port should match the one on step #1)
5. Write `/hello` to your new slack bot and let the magic begin

>*This is a development setup so you can quickly see your code changes in slack without the need to redeploy your whole site.
> Once your bot is ready for production you should update your commands url to a permanent one.
> [Heroku](https://duckduckgo.com/?q=flask+on+heroku&t=brave&ia=web) might be a good choice if you are just getting started as it has a generous free tier.

### Does it support new slack Shorcuts?
Yes, See [examples/shortcuts.py](examples/shortcuts.py) for a self contained example

### And can i use new slack Modals?
Of course! See [examples/views.py](examples/views.py) for a quick example

### Are interactive actions supported?
Yes! See [examples/actions.py](examples/actions.py) for a quickstart.
>Note: Legacy actions are unsupported by design as they are discouraged by slack. Nevertheless, if there's popular demand, we could add support for them.

### And slack events?
As you may have guessed, they are also supported. See [examples/events.py](examples/events.py) for an example.

## Dependency Injection
As you add more and more commands you will find yourself repeating yourself while parsing slack request on every function

The lib offers a solution to this with dependency injection.
```python
@slackify.command
def hello(command, command_args, response_url):
    return reply_text(f"You called `{command} {command_args}`. Use {response_url} for delayed responses")
```
Your view function will now get the request command, arguments and response_url for free! Pretty cool, right?

If you are a user of pytest, this idea is similar to pytest fixtures

See [examples/injection.py](examples/injection.py) for the full example


## Full example
Here you have a more complete example showcasing all functionality. It includes:
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
from slackify import (ACK, OK, Slackify, async_task, block_reply, request,
                      respond, text_block, Slack)

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
    """If a user clicks yes on the message above, execute this callback"""
    text_blok = text_block('Super! I do too :thumbsup:')
    respond(payload['response_url'], {'blocks': [text_blok]})
    return OK


@slackify.action("no")
def no(payload):
    """If a user clicks no on the hello message, execute this callback"""
    text_blok = text_block('Boo! You are so boring :thumbsdown:')
    respond(payload['response_url'], {'blocks': [text_blok]})
    return OK


@slackify.command
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


@slackify.view("registration_form")
def register_callback(payload):
    """Handle registration form submission."""
    response = payload['view']['state']['values']
    text_blok = text_block(f':heavy_check_mark: You are now registered.\nForm payload:\n```{response}```')
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
    send_message(cli, blocks=[text_block(msg)], user_id=payload['user']['id'])
    return ACK


@slackify.event('reaction_added')
def echo_reaction(payload):
    """If any user reacts to a message, also react with that emoji to the message"""
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
    cli.chat_postMessage(channel=event['channel'], text='Hi! 👋')
```

## Usage as a Blueprint
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

## API Reference
```python

@slackify.command
or
@slackify.command(name='custom')


@slackify.shortcut('shorcut-id')


@slackify.action('action_id')
or
@slackify.action(action_id='action_id', block_id='block_id')


@slackify.event('event_name') # See https://api.slack.com/events for all available events


# Shortcut for `message` events that match certain string or regex
@slackify.message('Hi!')
or
@slackify.message(re.compile(r'Bye|see you|xoxo'))


@slackify.view('callback_id')


# Specify what to do if a slack request doesn't match any of your handlers.
# By default it simply ignores the request.
@slackify.default

# Handle unexpected errors that occur inside handlers.
# By default returns status 500 and a generic message.
# The exception will be passed as a positional argument to the decorated function
@slackify.error
```


## How does it work?
If you are curious you may want to know how the lib works.

In fact there's really little to know and hopefully
you can understand it by browsing the code and this brief introduction.

The lib exposes a main class called `Slackify` that can either receive a Flask instance
as `app` argument or creates one on the fly.
It then binds two routes. One for commands, shortcuts, actions and another one for slack events.

The first route is `/` by default, it inspects the incoming requests and looks for any declared handler that is interested in handling this request to redirect it.

If it finds a handler, it injects any dependency the view may require as a view argument, and then call the view function, passing the return value as the request response.

If there's no match, it ignores the request and it follows the
normal request lifecycle.

If there's an error, an overridable function through `@slackify.error` is executed to show a friendly message.

The second route the lib adds is the events route at `/slack/events`.

When it receives a post request, it emits an event through `pyee.ExecutorEventEmitter` with the event type and quickly responds with the response acknowledgment slack requires to avoid showing an error to the user. This allows asynchronous execution of the function, while still responding quickly to slack.
In other words, when you decorate a function with `app.event('event_type')` what you are really doing is setting up a listener for the `event_type` that will receive the event payload. No magic.

If after reading this you have an idea of how we can extend or improve this lib in any way, it would be great to receive an issue or pull request!
I feel there's still a void on slack bots with python that java and javascript have covered with [bolt's](https://github.com/slackapi/bolt) beautiful API.
Below you can find the current roadmap of features i would like to include.
