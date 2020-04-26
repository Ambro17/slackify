# Flask-Slack
`Flask-Slack` is a framework to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

## Quickstart
```python
from flask_slack import Flack, async_task


app = Flack(__name__)


# That's it! now you can declare commands, shortcuts, actions, and whatever you please!
# No routing nightmare, no special endpoints, just declare what you want


@app.command
def hello():
    return 'Hello from Slack'


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
```


## What about new slack Shorcuts?
See [examples/shortcuts.py](examples/shortcuts.py) for a self contained example

## Are interactive actions supported?
Yes! See [examples/actions.py](examples/actions.py) for a self contained example

>Note: Legacy actions are not supported by design. But it could be implemented if users need it.