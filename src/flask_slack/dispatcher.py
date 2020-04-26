from typing import List, Optional
from flask import request
from dataclasses import dataclass
import json


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

    def get_payload(self, req):
        """Extract payload from request.form as dict"""
        if 'payload' not in request.form:
            return None

        return json.loads(request.form['payload'])


class Command(FormMatcher):
    def __init__(self, command):
        super().__init__()
        self.command = command

    def match(self, request):
        return super().match(request) and request.form.get('command') == f'/{self.command}'

    def endpoint(self):
        return self.command


@dataclass(eq=True, frozen=True)
class ActionFilter:
    action_id: str
    block_id: Optional[str] = None


class ActionMatcher(FormMatcher):
    def __init__(self, action_id, block_id=None, **kwargs):
        super().__init__()
        self.action_id = action_id
        self.block_id = block_id

    def match(self, request):
        if not super().match(request):
            return False
        payload = self.get_payload(request)
        if not payload:
            return False

        type = payload.get('type')
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
        return self.action_id


class ShortcutMatcher(FormMatcher):
    def __init__(self, shortcut_id):
        self.id = shortcut_id

    def match(self, req):
        if not super().match(req):
            return False
        payload = self.get_payload(req)
        if not payload:
            return False
        type = payload.get('type')
        callback = payload.get('callback_id')
        return type in ('shortcut', 'message_action') and callback == self.id

    def endpoint(self):
        return self.id


class ViewMatcher(FormMatcher):
    def __init__(self, view_id):
        self.id = view_id

    def match(self, req):
        if not super().match(req):
            return False

        payload = self.get_payload(req)
        if not payload:
            return False
        if 'view' not in payload:
            return False
        type = payload.get('type')
        callback = payload['view'].get('callback_id')
        return type == 'view_submission' and callback == self.id

    def endpoint(self):
        return self.id
