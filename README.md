# Flask-Slack
`Flask-Slack` is a light framework designed to accelerate your development of slack apps by letting you focus on **what you want** instead of fighting with *how to do it*

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


### What about new slack Shorcuts?
See [examples/shortcuts.py](examples/shortcuts.py) for a self contained example

### But can i use new slack Modals?
Of course! See [examples/views.py](examples/views.py) for a quick example

### Are interactive actions supported?
Yes! See [examples/actions.py](examples/actions.py) for a quickstart.
>Note: Legacy actions are unsupported by design as they are discouraged by slack. Nevertheless, if there's popular demand, we could add support for them.

### And slack events?
As you may have guessed, they are also supported. See [examples/events.py](examples/events.py) for an example.


## Full fledged example
If you wanna see the full dance, go ahead and look [examples/full.py](examples/full.py) for an example
of all available functionality including
- A register command that opens a modal
- A hello command that shows interactive buttons
- A shortcut to roll a dice and get a random number
- An event handler that echoes reactions to messages.

## Roadmap
1. Support for app factory pattern
2. Support for blueprints