import re
from slackify import Flack



def given_a_cli_with_a_message_handler(cli):
    app = cli.application

    @app.message('hello')
    def hi(payload):
        return 'hi'

    BYE = re.compile(r'bye|see you')
    @app.message(BYE)
    def bye(payload):
        return 'Bye!'

    return cli



def test_message_is_ignored_if_doesnt_match_regex(bare_client, mocker):
    cli = given_a_cli_with_a_message_handler(bare_client)
    cli.application.emitter = mocker.MagicMock()

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
    cli.application.emitter.emit.assert_called_with('message', data)
    # assert message was ignored


def test_message_is_captured_if_it_matches_regex(bare_client, mocker):
    cli = given_a_cli_with_a_message_handler(bare_client)

    cli.application.emitter = mocker.MagicMock()
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
    assert cli.application.emitter.emit.called
    cli.application.emitter.emit.assert_called_with('message', data)


def test_message_is_captured_if_it_matches_precompiled_regex(bare_client):
    cli = given_a_cli_with_a_message_handler(bare_client)

    message = 'abc bye fgh'
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
