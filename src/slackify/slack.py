import json
import requests
import re


from .tasks import async_task


"""Acknowledge we received slack's interaction payload"""
OK = '', 200
ACK = OK

JSON_TYPE = {'Content-Type': 'application/json'}

RE_PATTERN = type(re.compile(r''))  # py3.6 does not have re.Pattern :(


def reply_text(text: str):
    """Helper method that returns a plain text response to slack"""
    return json.dumps({'text': text}), 200, JSON_TYPE


def reply(body: dict):
    """Helper method that returns a complex response to slack

    It may contain a blocks payload. A simple text structure or
    whatever slack admits as a valid response to certain action.
    It does nothing fancy. Just transforms dict to json, and
    passes json as Content-Type as slack requires.
    """
    return json.dumps(body), 200, JSON_TYPE


def text_block(text: str, markdown=True):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn" if markdown else 'plain_text',
            "text": text
        }
    }


def block_reply(blocks: list):
    return json.dumps({'blocks': blocks}), 200, JSON_TYPE


@async_task
def respond(url: str, message: str):
    """Respond async to interaction to allow fast acknowledge of interactive message request"""
    return requests.post(url, json=message, timeout=5)
