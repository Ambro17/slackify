from slackify import block_reply, reply_text, text_block, reply


def test_block_reply():
    assert block_reply([1, 2, 3]) == (
        '{"blocks": [1, 2, 3]}',
        200,
        {'Content-Type': 'application/json'}
    )


def test_reply_text():
    assert reply_text('hello') == (
        '{"text": "hello"}',
        200,
        {'Content-Type': 'application/json'}
    )


def test_reply_works_with_blocks_input():
    assert reply({'text': 'hello'}) == (
        '{"text": "hello"}',
        200,
        {'Content-Type': 'application/json'}
    )


def test_reply_works_with_text_input():
    assert reply({'blocks': [1, 2]}) == (
        '{"blocks": [1, 2]}',
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
