import requests

from .tasks import async_task


"""Acknowledge we received slack's interaction payload"""
OK = '', 200
ACK = OK


def reply(text):
    return {
        'text': text
    }


@async_task
def respond(url, message):
    """Respond async to interaction to allow fast acknowledge of interactive message request"""
    return requests.post(url, json=message, timeout=5)


def text_block(text, markdown=True):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn" if markdown else 'plain_text',
            "text": text
        }
    }
