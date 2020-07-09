from flask import Flask
from slackify import Slackify, request, Slack
import json


# Important! Before running set FLASK_APP=examples.async_task:app
app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack('xoxb-SECRET-bot-token')


@slackify.shortcut('funny_joke')
def tell_joke():
    payload = json.loads(request.form['payload'])
    user = payload['user']
    name = user.get('username', user.get('id'))
    cli.chat_postMessage(channel='#general', text=f'Knock Knock `{name}`')
    return '', 200
