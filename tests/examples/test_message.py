import re
from collections import defaultdict

import pytest
from pyee import BaseEventEmitter

from slackify import Flack


def given_a_cli_with_message_handlers(cli):
    app = cli.application

    # Used as functions instead of decorator to
    # Allow asserting being called
    @app.message('hello')
    def hi():
        return 'Hi!'

    @app.message(re.compile(r'bye|see you'))
    def bye():
        return 'Bye!'

    return cli


class FakeEmitter(BaseEventEmitter):
    """Testing interface for pyee event emitter"""

    def __init__(self):
        super().__init__()
        self.listeners = defaultdict(list)
        self.results = []


    def on(self, event, func):
        self.listeners[event].append(func)

    def emit(self, event, *args, **kwargs):
        """Sync implementation of emit to ease testing."""
        callbacks = self.listeners.get(event, [])
        for callback in callbacks:
            self.results.append(callback(*args, **kwargs))


def test_message_is_ignored_if_doesnt_match_regex(bare_client, mocker):
    emitter = FakeEmitter()
    bare_client.application.emitter = emitter
    cli = given_a_cli_with_message_handlers(bare_client)

    message = 'Not a match'
    data = {
        "event": {
            "type": "message",
            "channel": "C2147483705",
            "user": "U1234",
            "text": message,
            "ts": "1355517523.000005"
        },
        "type": "event_callback",
    }
    rv = cli.post('/slack/events', json=data, content_type='application/json')
    assert rv.status_code == 200
    # Assert both callbacks were replaced by bare return. Thus the None result.
    assert emitter.results == [None, None]


def test_message_is_captured_if_it_matches_regex(bare_client, mocker):
    emitter = FakeEmitter()
    bare_client.application.emitter = emitter
    cli = given_a_cli_with_message_handlers(bare_client)

    message = 'hello'
    data = {
        "event": {
            "type": "message",
            "channel": "C2147483705",
            "user": "U1234",
            "text": message,
            "ts": "1355517523.000005"
        },
        "type": "event_callback",
    }
    rv = cli.post('/slack/events',
                  json=data,
                  content_type='application/json')

    assert rv.data == b''
    assert rv.status == '200 OK'
    assert emitter.results == ['Hi!', None]


def test_message_is_captured_if_it_matches_precompiled_regex(bare_client, mocker):
    emitter = FakeEmitter()
    bare_client.application.emitter = emitter
    cli = given_a_cli_with_message_handlers(bare_client)

    message = 'abc see you fgh'
    data = {
        "event": {
            "type": "message",
            "channel": "C2147483705",
            "user": "U1234",
            "text": message,
            "ts": "1355517523.000005"
        },
        "type": "event_callback",
    }
    rv = cli.post('/slack/events', json=data, content_type='application/json')
    assert rv.status_code == 200
    assert rv.data == b''
    assert emitter.results == [None, 'Bye!']


def test_invalid_message_usage(bare_client):
    app = bare_client.application
    with pytest.raises(TypeError, match="'message' must be either str or a compiled regex."):
        @app.message(b'123')
        def try_it(payload):
            pass

    with pytest.raises(TypeError, match="'message' must be either str or a compiled regex."):
        @app.message(123)
        def try_it(payload):
            pass

    with pytest.raises(TypeError, match=r"message\(\) missing 1 required positional argument: 'message'"):
        @app.message()
        def try_it(payload):
            pass

    with pytest.raises(TypeError, match=r"'message' must be either str or a compiled regex. Not <class 'function'>"):
        @app.message
        def try_it(payload):
            pass


def test_message_not_expecting_payload_arg_should_fail(bare_client):
    app = bare_client.application


    with pytest.raises(
        TypeError, 
        match=f"Invalid signature for 'bad_function_missing_payload_arg'. Must expect one and only one positional argument"
    ):
        @app.message('hi')
        def bad_function_missing_payload_arg():
            pass


def test_event_handler_not_expecting_payload_arg_should_fail(bare_client):
    app = bare_client.application


    with pytest.raises(
        TypeError, 
        match=f"Invalid signature for 'your_func'. Must expect one and only one positional argument"
    ):
        @app.event('bla')
        def your_func():
            pass
