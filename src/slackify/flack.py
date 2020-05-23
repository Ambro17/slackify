from inspect import signature
import logging
import re

from flask import Flask, _request_ctx_stack, request, make_response
from pyee import ExecutorEventEmitter

from .dispatcher import ActionMatcher, Command, Dispatcher, ShortcutMatcher, ViewMatcher
from .slack import RE_PATTERN


logger = logging.getLogger(__name__)


class Slackify:

    _endpoint = ''

    def __init__(
        self,
        endpoint='/',
        events_endpoint='/slack/events',
        app=None,
        emitter=None,
        dispatcher=None,
        **kwargs
    ):
        self.app = app or Flask(__name__)
        self._configure_app(endpoint, events_endpoint)
        self.dispatcher = dispatcher or Dispatcher()
        self.emitter = emitter or ExecutorEventEmitter()

    def _configure_app(self, endpoint, events_endpoint):
        """Configure app to redirect slack requests if they match a registered handler"""
        # Listen for each request and redirect it if there's a matching handler
        self.app.before_request(self._redirect_slack_requests)
        self._endpoint = endpoint
        self._bind_main_entrypoint(endpoint)
        self._bind_events_entrypoint(events_endpoint)

    def _bind_main_entrypoint(self, endpoint):
        self.app.add_url_rule(endpoint, 'slackify_entrypoint', lambda: 'Slackify Home', methods=('GET', 'POST'))

    def _bind_events_entrypoint(self, events_endpoint):
        self.app.add_url_rule(events_endpoint, 'slackify_events', self._handle_event, methods=('POST',))

    def _handle_event(self):
        """Respond to event request sync and emit event for async event handling"""
        event_data = request.get_json()
        # Respond to slack challenge to enable our endpoint as an event receiver
        if "challenge" in event_data:
            return make_response(
                event_data.get("challenge"), 200, {"Content-Type": "application/json"}
            )

        if "event" in event_data:
            event_type = event_data["event"]["type"]
            self.emitter.emit(event_type, event_data)
            return make_response("", 200)

    def _redirect_slack_requests(self):
        request = _request_ctx_stack.top.request
        if request.routing_exception is not None:
            self.app.raise_routing_exception(request)

        if not self._should_handle_request(request):
            return

        try:
            endpoint = self.dispatcher.match(request)
        except StopIteration:
            logger.info('No handler matched this request')
            return self._handle_unknown()
        except Exception as e:
            logger.exception('Something bad happened.')
            return self._handle_error(e)

        rule = request.url_rule
        rule.endpoint = endpoint

    def _should_handle_request(self, req):
        return req.method == 'POST' and request.path == self._endpoint

    def default(self, func):
        self._handle_unknown = func

    def _handle_unknown(self):
        """Ignore unknown commands by default."""
        return None

    def error(self, func):
        self._handle_error = func

    def _handle_error(self, e):
        return self.app.make_response(('Something went wrong..', 500))

    def shortcut(self, callback_id, **options):
        def register_handler(shortcut_handler):
            command = callback_id
            self.app.add_url_rule(f'/{command}', command, shortcut_handler, **options)
            self.dispatcher.add_matcher(ShortcutMatcher(command))
            return shortcut_handler

        return register_handler

    def command(self, func=None, **options):
        """A decorator that is used to register a function as a command handler.

           It can be used as a plain decorator or as a parametrized decorator factory.
           This does the same as `add_command_handler`

        Usage:
            >>>@command
            >>>def hola():
            >>>    print('hola', kwargs)


            >>>@command(name='goodbye')
            >>>def chau():
            >>>    print('chau', kwargs)
        """
        def decorate(func):
            command = options.pop('name', func.__name__)
            rule = f'/{command}' if not command.startswith('/') else command
            self.app.add_url_rule(rule, command, func, **options)
            self.dispatcher.add_matcher(Command(command))
            return func

        used_as_plain_decorator = bool(func)
        if used_as_plain_decorator:
            return decorate(func)
        else:
            return decorate

    def action(self, action_id=None, **options):
        if action_id is None and options.get('block_id') is None or callable(action_id):
            raise TypeError("action() missing 1 required positional argument: 'action_id'")

        def decorate(func):
            block_id = options.pop('block_id', None)
            command = action_id or block_id  # TODO: Handle special characters that make url rule invalid?
            self.app.add_url_rule(f'/{command}', command, func, **options)
            self.dispatcher.add_matcher(ActionMatcher(command, block_id=block_id))
            return func

        return decorate

    def view(self, view_callback_id, **options):
        def decorate(func):
            self.app.add_url_rule(f'/{view_callback_id}', view_callback_id, func, **options)
            self.dispatcher.add_matcher(ViewMatcher(view_callback_id))
            return func

        return decorate

    def event(self, event, func=None):

        def add_listener(func):
            if len(signature(func).parameters) != 1:
                error = f"Invalid signature for '{func.__name__}'. Must expect one and only one positional argument"
                raise TypeError(error)

            self.emitter.on(event, func)

        return add_listener(func) if func else add_listener

    def message(self, message, func=None, **kwargs):
        msg_regex = re.compile(message) if isinstance(message, str) else message
        if not isinstance(msg_regex, RE_PATTERN):
            raise TypeError(f"'message' must be either str or a compiled regex. Not {type(msg_regex)!r}")

        def quit_if_no_match(user_handler, regex, event_payload):
            """Quit listener execution if event text doesn't match the specified regex."""
            text = event_payload['event'].get('text', '')
            if not regex.search(text):
                return

            return user_handler(event_payload)

        def decorate(func):
            if len(signature(func).parameters) != 1:
                error = f"Invalid signature for '{func.__name__}'. Must expect one and only one positional argument"
                raise TypeError(error)

            listener = lambda payload: quit_if_no_match(func, msg_regex, payload)  # noqa: sh!
            self.event('message', listener)
            return func

        return decorate(func) if func else decorate


class Flack(Flask):

    def __init__(self, import_name, endpoint='/', events_endpoint='/slack/events', **kwargs):
        super().__init__(import_name, **kwargs)
        self.dispatcher = Dispatcher()
        self.before_request_funcs.setdefault(None, []).append(self._redirect_requests)
        self.emitter = ExecutorEventEmitter()
        self._endpoint = endpoint
        self._bind_main_entrypoint(endpoint)
        self._bind_events_entrypoint(events_endpoint)

    def shortcut(self, callback_id, **options):
        def decorate(func):
            command = callback_id
            self.add_url_rule(f'/{command}', command, func, **options)
            self.dispatcher.add_matcher(ShortcutMatcher(command))
            return func

        return decorate

    def command(self, func=None, **options):
        """A decorator that is used to register a function as a command handler.

           It can be used as a plain decorator or as a parametrized decorator factory.
           This does the same as `add_command_handler`

        Usage:
            >>>@command
            >>>def hola():
            >>>    print('hola', kwargs)


            >>>@command(name='goodbye')
            >>>def chau():
            >>>    print('chau', kwargs)
        """
        def decorate(func):
            command = options.pop('name', func.__name__)
            rule = f'/{command}' if not command.startswith('/') else command
            self.add_url_rule(rule, command, func, **options)
            self.dispatcher.add_matcher(Command(command))
            return func

        used_as_plain_decorator = bool(func)
        if used_as_plain_decorator:
            return decorate(func)
        else:
            return decorate

    def action(self, action_id=None, **options):
        if action_id is None and options.get('block_id') is None or callable(action_id):
            raise TypeError("action() missing 1 required positional argument: 'action_id'")

        def decorate(func):
            block_id = options.pop('block_id', None)
            command = action_id or block_id  # TODO: Handle special characters that make url rule invalid?
            self.add_url_rule(f'/{command}', command, func, **options)
            self.dispatcher.add_matcher(ActionMatcher(command, block_id=block_id))
            return func

        return decorate

    def view(self, view_callback_id, **options):
        def decorate(func):
            self.add_url_rule(f'/{view_callback_id}', view_callback_id, func, **options)
            self.dispatcher.add_matcher(ViewMatcher(view_callback_id))
            return func

        return decorate

    def event(self, event, func=None):

        def add_listener(func):
            if len(signature(func).parameters) != 1:
                error = f"Invalid signature for '{func.__name__}'. Must expect one and only one positional argument"
                raise TypeError(error)
            self.emitter.on(event, func)

        return add_listener(func) if func else add_listener

    def message(self, message, func=None, **kwargs):
        msg_regex = re.compile(message) if isinstance(message, str) else message
        if not isinstance(msg_regex, RE_PATTERN):
            raise TypeError(f"'message' must be either str or a compiled regex. Not {type(msg_regex)!r}")

        def quit_if_no_match(user_handler, regex, event_payload):
            """Quit listener execution if event text doesn't match the specified regex."""
            text = event_payload['event'].get('text', '')
            if not regex.search(text):
                return

            return user_handler(event_payload)

        def decorate(func):
            if len(signature(func).parameters) != 1:
                error = f"Invalid signature for '{func.__name__}'. Must expect one and only one positional argument"
                raise TypeError(error)

            listener = lambda payload: quit_if_no_match(func, msg_regex, payload)  # noqa: sh!
            self.event('message', listener)
            return func

        return decorate(func) if func else decorate

    def default(self, func):
        self._handle_unknown = func

    def _handle_unknown(self):
        """Ignore unknown commands by default."""
        return None

    def error(self, func):
        self._handle_error = func

    def _handle_error(self, e):
        return self.make_response(('Oops..', 500))

    def _redirect_requests(self):
        request = _request_ctx_stack.top.request
        if request.routing_exception is not None:
            self.raise_routing_exception(request)

        if request.method == 'GET' or request.path != self._endpoint:
            return

        try:
            endpoint = self.dispatcher.match(request)
        except StopIteration:
            logger.info('No handler matched this request')
            return self._handle_unknown()
        except Exception as e:
            logger.exception('Something bad happened.')
            return self._handle_error(e)

        rule = request.url_rule
        rule.endpoint = endpoint

    def _bind_main_entrypoint(self, endpoint):
        self.add_url_rule(endpoint, '_entrypoint', lambda: 'Home', methods=('GET', 'POST'))

    def _bind_events_entrypoint(self, endpoint):
        self.add_url_rule(endpoint, '_slack_events', self._handle_event, methods=('POST',))

    def _handle_event(self):
        """Respond to event request sync and emit event for async event handling"""
        event_data = request.get_json()
        # Respond to slack challenge to enable our endpoint as an event receiver
        if "challenge" in event_data:
            return make_response(
                event_data.get("challenge"), 200, {"Content-Type": "application/json"}
            )

        if "event" in event_data:
            event_type = event_data["event"]["type"]
            self.emitter.emit(event_type, event_data)
            return make_response("", 200)
