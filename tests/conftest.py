import pytest
from src.flask_slack.flack import Flack


@pytest.fixture
def client(test_app):
    test_app.config['TESTING'] = True

    with test_app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def test_app():
    app = Flack('testing')

    @app.command(name='chau')
    def hello():
        return 'Hello'

    @app.shortcut('my-shortcut')
    def shortcut():
        return 'Shortcut'

    @app.action(id='my-action-id')
    def my_action():
        return 'Action'

    return app
