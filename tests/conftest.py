import pytest
from slackify import Slackify


@pytest.fixture
def client(test_app):
    test_app.config['TESTING'] = True

    with test_app.test_client() as client:
        yield client


@pytest.fixture
def bare_client():
    app = Slackify()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def test_app():
    app = Slackify()

    @app.command(name='chau')
    def hello():
        return 'Hello'

    @app.command
    def goodbye():
        return 'Bye'

    @app.shortcut('my-shortcut')
    def shortcut():
        return 'Shortcut'

    @app.action('my-action-id')
    def my_action():
        return 'Action'

    @app.action(action_id='the-id', block_id='a-block-id')
    def complex_action():
        return 'Complex Action'

    @app.view('my-first-view')
    def my_view():
        return 'View'

    @app.default
    def unknown_command():
        return 'Unknown Command'

    @app.event('reaction_added')
    def react_to_reaction(payload):
        return '🐍'

    return app.app


@pytest.fixture
def slackify_test():
    app = Slackify()

    @app.event('reaction_added')
    def react_to_reaction(payload):
        return '🐍'

    return app
