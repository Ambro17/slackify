from slackify import Slackify
from flask import Blueprint, Flask
import pytest


@pytest.fixture
def client():
    bp = Blueprint('TestBlueprint', __name__, url_prefix='/blueprintBla')
    slackify = Slackify(app=bp, endpoint='/')

    @slackify.command(methods=('POST', 'GET'))  # TODO> Remove post, replace by redirecting.
    def hello():
        return 'Hello from blueprint'

    app = Flask('Main')
    app.register_blueprint(bp)
    print(app.url_map)

    with app.test_client() as cli:
        yield cli


def test_blueprint_url_must_be_provided_with_trailing_slash(client):
    pass


def test_blueprint_home_responds_with_default_message(client):
    rv = client.post('/blueprintBla/', data={'bla': 1}, content_type='application/x-www-form-urlencoded')
    assert b'Slackify Home' == rv.data


def test_blueprint_home_responds_with_default_message(client):
    rv = client.post('/blueprintBla/', data={'command': '/hello'}, content_type='application/x-www-form-urlencoded')
    assert b'Hello from blueprint' == rv.data


def test_command_works_when_blueprint_is_provided_on_initialization(client):
    rv = client.post('/blueprintBla/hello', data={'command': '/hello'}, content_type='application/x-www-form-urlencoded')
    assert b'Hello from blueprint' == rv.data, rv.data
