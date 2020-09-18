import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import flask


class Matcher(ABC):
    """Match interface to capture a specific request"""

    @abstractmethod
    def match(self, request: flask.Request) -> bool:
        """Determine if a request should be handled by this matcher"""

    @abstractmethod
    def endpoint(self):
        """Flask view endpoint"""


class Dispatcher:
    """Dispatch requests based on its shape"""

    matchers: List[Matcher] = []

    def add_matcher(self, matcher: Matcher):
        """Add a new request matcher to handle incoming slack requests"""
        self.matchers.append(matcher)

    def match(self, request: flask.Request) -> bool:
        """Find a matcher that handle the request. Raises StopIteration if not found"""
        return next(
            matcher.endpoint()
            for matcher in self.matchers
            if matcher.match(request)
        )


class FormMatcher(Matcher):
    def match(self, request) -> bool:
        return 'application/x-www-form-urlencoded' in request.headers.get('Content-Type', '')

    def get_payload(self, request: flask.Request) -> Optional[Dict[str, Any]]:
        """Extract payload from request.form as dict"""
        if 'payload' not in request.form:
            return None

        return json.loads(request.form['payload'])


class Command(FormMatcher):
    def __init__(self, command):
        super().__init__()
        self.command = command

    def match(self, request: flask.Request) -> bool:
        return super().match(request) and request.form.get('command') == f'/{self.command}'

    def endpoint(self) -> str:
        return self.command


class ActionMatcher(FormMatcher):
    def __init__(self, action_id: str, block_id: Optional[str] = None, **kwargs: Dict[str, Any]):
        super().__init__()
        self.action_id = action_id
        self.block_id = block_id

    def match(self, request: flask.Request) -> bool:
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

    def endpoint(self) -> str:
        return self.action_id


class ShortcutMatcher(FormMatcher):
    def __init__(self, shortcut_id: str):
        self.id = shortcut_id

    def match(self, request: flask.Request) -> bool:
        if not super().match(request):
            return False
        payload = self.get_payload(request)
        if not payload:
            return False
        type = payload.get('type')
        callback = payload.get('callback_id')
        return type in ('shortcut', 'message_action') and callback == self.id

    def endpoint(self) -> str:
        return self.id


class ViewMatcher(FormMatcher):
    def __init__(self, view_id):
        self.id = view_id

    def match(self, request: flask.Request) -> bool:
        if not super().match(request):
            return False
        payload = self.get_payload(request)
        if not payload:
            return False
        if 'view' not in payload:
            return False
        type = payload.get('type')
        callback = payload['view'].get('callback_id')
        return type == 'view_submission' and callback == self.id

    def endpoint(self) -> str:
        return self.id
