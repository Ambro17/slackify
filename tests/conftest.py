import pytest
from flask import Flask
from slackify import Slackify


@pytest.fixture
def client(test_app):
    test_app.config['TESTING'] = True

    with test_app.test_client() as client:
        yield client


@pytest.fixture
def bare_app():
    return Slackify()


@pytest.fixture
def bare_client(bare_app):
    bare_app.app.config['TESTING'] = True

    with bare_app.app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def test_app():
    app = Flask(__name__)
    slackify = Slackify(app=app)

    @slackify.command(name='chau')
    def hello():
        return 'Hello'

    @slackify.command
    def goodbye():
        return 'Bye'

    @slackify.shortcut('my-shortcut')
    def shortcut():
        return 'Shortcut'

    @slackify.action('my-action-id')
    def my_action():
        return 'Action'

    @slackify.action(action_id='the-id', block_id='a-block-id')
    def complex_action():
        return 'Complex Action'

    @slackify.view('my-first-view')
    def my_view():
        return 'View'

    @slackify.default
    def unknown_command():
        return 'Unknown Command'

    @slackify.event('reaction_added')
    def react_to_reaction(payload):
        return '🐍'

    return app


@pytest.fixture
def slackify_test():
    app = Flask(__name__)
    slackify = Slackify(app=app)

    @slackify.event('reaction_added')
    def react_to_reaction(payload):
        return '🐍'

    return slackify
