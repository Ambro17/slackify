import requests

from .tasks import async_task


def reply(text):
    return {
        'text': text
    }


@async_task
def respond(url, message):
    """Respond async to interaction to allow fast acknowledge of interactive message request"""
    return requests.post(url, json=message, timeout=5)
