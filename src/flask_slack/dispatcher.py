from typing import List, Optional
from flask import request
from dataclasses import dataclass


class Matcher:
    """Match interface to capture a specific request"""
    def match(self, request):
        pass


class Dispatcher:
    """Dispatch requests based on its shape"""

    matchers: List[Matcher] = []

    def add_matcher(self, matcher):
        self.matchers.append(matcher)

    def match(self, request):
        return next(
            matcher.endpoint()
            for matcher in self.matchers
            if matcher.match(request)
        )


class JSONMatcher:
    def match(self, request):
        return request.headers.get('Content-Type') == 'application/json'


class FormMatcher:
    def match(self, request):
        return 'application/x-www-form-urlencoded' in request.headers.get('Content-Type', '')


class Command(FormMatcher):
    def __init__(self, command):
        super().__init__()
        self.command = command

    def match(self, request):
        return super().match(request) and request.form['command'] == f'/{self.command}'

    def endpoint(self):
        return self.command


@dataclass(eq=True, frozen=True)
class ActionFilter:
    action_id: str
    block_id: Optional[str] = None


class ActionMatcher(JSONMatcher):
    def __init__(self, action_id, block_id=None, **kwargs):
        super().__init__()
        self.action_id = action_id
        self.block_id = block_id

    def match(self, request):
        if not super().match(request):
            return False
        payload = request.get_json()['payload']
        type = payload['type']
        if type != 'block_actions':  # TODO: Generalize in base class
            return False
        if 'actions' not in payload:
            return False

        action = payload['actions'][0]
        action_id = action['action_id']
        block_id = action['block_id']
        if not self.block_id:
            # Only action id was specified, so we just compare by that.
            matches = self.action_id == action_id
        else:
            matches = self.action_id == action_id and self.block_id == block_id

        return matches

    def endpoint(self):
        return f'{self.action_id}'


class ShortcutMatcher(JSONMatcher):
    def __init__(self, shortcut_id):
        self.id = shortcut_id

    def match(self, req):
        if not super().match(req):
            return False

        payload = request.get_json()['payload']
        type = payload.get('type')
        callback = payload.get('callback_id')
        return type in ('shortcut', 'message_action') and callback == self.id

    def endpoint(self):
        return self.id


dp = Dispatcher()
