from slackify import Flack, request, reply_text

app = Flack(__name__)


@app.command
def hello():
    form = request.form['command']
    text = request.form['text']
    return reply_text(f'You called `{form} {text}`')


@app.command(name='bye')
def goodbye():
    return reply_text(f'Goodbye')
