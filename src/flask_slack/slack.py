import requests
from flask import jsonify

from .tasks import async_task


"""Acknowledge we received slack's interaction payload"""
OK = '', 200
ACK = OK


def reply(text):
    return jsonify({
        'blocks': [text_block(text)]
    })


def text_block(text, markdown=True):
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn" if markdown else 'plain_text',
            "text": text
        }
    }


def block_reply(blocks):
    return jsonify({'blocks': blocks})


@async_task
def respond(url, message):
    """Respond async to interaction to allow fast acknowledge of interactive message request"""
    return requests.post(url, json=message, timeout=5)
