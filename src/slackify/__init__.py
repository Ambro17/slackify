"""`Slackify` provides a declarative API to register handlers for Slack

- Commands
- Actions
- Events
- Shorcuts
- Modals
- Messages

Its main focus is to make the task of developing slack bots _fun and fast_.

That's why it tries to hide all implementation details and offer a clean
_flask-like_ decorator syntax.

Hopefully, this will allow you to focus on the workflows you want to support,
instead of struggling with routing or payload details.

.. include:: ../../README.md
"""

from flask import *  # noqa: Expose all flask objects as top level imports
from flask import request

from .main import Slackify
from .blueprint import Blueprint
from .slack import Slack, ACK, OK, block_reply, reply_text, reply, respond, text_block
from .tasks import async_task

__all__ = [
    'Slackify',
    'Blueprint',
    'Slack',
    'request',
    'reply_text',
    'reply',
    'block_reply',
    'respond',
    'text_block',
    'async_task',
    'OK',
    'ACK',
]
