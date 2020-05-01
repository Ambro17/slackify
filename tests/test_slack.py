from flask_slack.slack import block_reply, reply, text_block


def test_block_reply():
    assert block_reply([1, 2, 3]) == (
        '{"blocks": [1, 2, 3]}',
        200,
        {'Content-Type': 'application/json'}
    )


def test_reply():
    assert reply('hello') == (
        '{"text": "hello"}',
        200,
        {'Content-Type': 'application/json'}
    )


def test_text_block():
    assert text_block('message') == {
        "type": "section",
        "text": {
            "type": 'mrkdwn',
            "text": 'message'
        }
    }

    assert text_block('message', markdown=False) == {
        "type": "section",
        "text": {
            "type": 'plain_text',
            "text": 'message'
        }
    }
