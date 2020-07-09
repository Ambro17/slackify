from flask import Flask
from slackify import Slackify, request, reply_text

# Important! Before running set FLASK_APP=examples.async_task:app
app = Flask(__name__)
slackify = Slackify(app=app)


@slackify.command
def hello():
    form = request.form['command']
    text = request.form['text']
    return reply_text(f'You called `{form} {text}`')


@slackify.command(name='bye')
def goodbye():
    return reply_text('Goodbye')
