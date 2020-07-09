# slack_blueprint.py
from slackify import Slackify, Blueprint, reply_text

bp = Blueprint('slackify_bp', __name__, url_prefix='/slack')
slackify = Slackify(app=bp)


@slackify.command
def hello():
    return reply_text('Hello from a blueprint')


# app.py
from flask import Flask                                 # noqa: Ignore E402, as it is an example
# from slack_blueprint import bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
