from flask_slack import Flack, request, jsonify

app = Flack(__name__)


@app.command
def hello():
    form = request.form['command']
    text = request.form['text']
    return jsonify({
        'text': f'You called `{form} {text}`'
    })


@app.command(name='abc')
def goodbye():
    return jsonify({
        'text': f'Mandril'
    })
