from slackify import Flack, request, Slack
import json


app = Flack(__name__)
cli = Slack('xoxb-SECRET-bot-token')


@app.shortcut('funny_joke')
def tell_joke():
    payload = json.loads(request.form['payload'])
    user = payload['user']
    name = user.get('username', user.get('id'))
    cli.chat_postMessage('#general', text=f'Knock Knock `{name}`')
    return '', 200
