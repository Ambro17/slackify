# Flask-Slack
`Flask-Slack` is a framework to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

# Usage
```
from flask_slack import Flack, Dispatcher, async_task, respond


# Create your slack app with the events dispatcher
dp = Dispatcher()
app = Flack(__name__)


# That's it! now you can declare commands, shortcuts, interactive actions handlers, and whatever you please!
# No routing nightmare, no special endpoints, just declare what you want


@app.command
def hello():
    return 'Hello'


# Change the slash command name to /say_bye instead of the default function name
@app.command(name='say_bye')
def bye():
    my_background_job()
    return 'Bye'


@async_task
def my_background_job():
    """Non blocking long task"""
    sleep(15)
    return


@app.shortcut('my-shortcut')
def shortcut():
    return respond('Shortcut')


@app.action('my-action-id')
def action():
    return 'You clicked a button'


@app.view('my-modal-id')
def open_modal():
    return 'Here is your modal!'
```
