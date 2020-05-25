from slackify import Slackify, request, reply_text

# Important! Before running set FLASK_APP=examples.async_task:app.app
app = Slackify()


@app.command
def hello():
    form = request.form['command']
    text = request.form['text']
    return reply_text(f'You called `{form} {text}`')


@app.command(name='bye')
def goodbye():
    return reply_text(f'Goodbye')
