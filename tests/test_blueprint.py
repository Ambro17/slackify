import pytest
from flask import Flask

from slackify import Slackify, Blueprint


def test_we_can_add_a_custom_endpoint_besides_blueprint_prefix():
    bp = Blueprint('TestBlueprint', __name__, url_prefix='/blueprintBla')
    slackify = Slackify(app=bp, endpoint='/slack')

    @slackify.command
    def hello():
        return 'Hello from special endpoint'

    app = Flask('Bare')
    app.register_blueprint(bp)

    client = app.test_client()
    rv = client.post('/blueprintBla/slack',
                     data={'command': '/hello'},
                     content_type='application/x-www-form-urlencoded')
    assert rv.status == '200 OK'
    assert rv.data == b'Hello from special endpoint'


def test_we_cant_use_a_bp_with_no_url_prefix():
    with pytest.raises(ValueError, match="Missing required 'url_prefix' for blueprint TestBlueprint"):
        no_prefix_bp = Blueprint('TestBlueprint', __name__)
        Slackify(app=no_prefix_bp)


@pytest.fixture(scope='module')
def client():
    bp = Blueprint('TestBlueprint', __name__, url_prefix='/blueprintBla')
    slackify = Slackify(app=bp)

    @slackify.command
    def hello():
        return 'Hello from blueprint'

    @slackify.command(methods=('POST', 'GET'))
    def bye():
        return 'Bye from blueprint'

    app = Flask('Main')
    app.register_blueprint(bp)

    with app.test_client() as cli:
        yield cli


def test_blueprint_url_must_be_provided_with_trailing_slash(client):
    rv = client.post('/blueprintBla', data={'bla': 1}, content_type='application/x-www-form-urlencoded')
    assert rv.status == '308 PERMANENT REDIRECT'
    assert rv.headers['location'] == 'http://localhost/blueprintBla/'


def test_blueprint_home_responds_with_default_message(client):
    rv = client.post('/blueprintBla/', data={'bla': 1}, content_type='application/x-www-form-urlencoded')
    assert '🚀 Slackify Home' in rv.data.decode('utf-8')


def test_post_to_main_endpoint_redirects_on_command_argument(client):
    rv = client.post('/blueprintBla/', data={'command': '/hello'}, content_type='application/x-www-form-urlencoded')
    assert b'Hello from blueprint' == rv.data


def test_direct_post_to_command_url_fails_if_not_explicitly_allowed(client):
    rv = client.post('/blueprintBla/hello', content_type='application/x-www-form-urlencoded')
    assert rv.status == '405 METHOD NOT ALLOWED'


def test_direct_post_to_command_url_works_when_explicitly_defined(client):
    rv = client.post('/blueprintBla/bye', content_type='application/x-www-form-urlencoded')
    assert b'Bye from blueprint' == rv.data
