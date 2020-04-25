# Flask-Slack
`Flask-Slack` is a framework to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

# Usage
```
from flask_slack import Flack, Dispatcher, ack, respond, async_task

dp = Dispatcher()
app = Flack(__name__, dispatcher=dp)


@app.command
def hello():
    return 'Hello'


@app.command(name='say_bye')
def bye():
    do_something_long()
    return 'Bye'

@async_task
def do_something_long():
    sleep(15)
    return

@app.shortcut('my-shortcut')
def shortcut():
    return 'Shortcut'


@app.action('my-action-id')
def action():
    return 'You clicked a button'


@app.view('my-modal-id')
def action():
    return 'Here is your modal!'



```
