from typing import Callable, Union

from slackify.injection import Injector, injector as builtin_injector
from inspect import signature
import logging
import re

from flask import Flask, _request_ctx_stack, request, make_response, Blueprint, Response  # type: ignore
import pyee  # type: ignore

from .dispatcher import ActionMatcher, Command, Dispatcher, ShortcutMatcher, ViewMatcher
from .slack import RE_PATTERN


logger = logging.getLogger(__name__)


class Slackify:
    """:class:`Slackify` is the orchestrator of the slack dance

    It has two main responsabilities:
        1. Registering callbacks for slack requests.
        2. Dispatch incoming requests to the registered callback.

    Args:
        app (Union[Flask, Blueprint]): Flask instance or Blueprint which will be used to register callbacks
        endpoint (str): Endpoint to expose in slack requests for automatic redirection
        events_endpoint (str): Endpoint to expose as slack events listener
        emitter (pyee.BaseEventEmitter): Class in charge of emitting events
        dispatcher (Dispatcher): Class in charge of adding and dispatching slack requests
        injector (Injector): Class in charge of injecting arguments to callback functions
    """

    _endpoint = ''

    def __init__(
        self,
        app: Union[Flask, Blueprint, None] = None,
        endpoint: str = '/',
        events_endpoint: str = '/slack/events',
        emitter: pyee.BaseEventEmitter = None,
        dispatcher: Dispatcher = None,
        injector: Injector = None,
        **kwargs
    ):
        self.app = app or Flask(__name__)
        self._configure_app(endpoint, events_endpoint)
        self.dispatcher = dispatcher or Dispatcher()
        self.emitter = emitter or pyee.ExecutorEventEmitter()
        self.injector = injector or builtin_injector

    def _configure_app(self, endpoint, events_endpoint):
        """Configure app to redirect slack requests if they match a registered handler"""
        # Listen for each request and redirect it if there's a matching handler
        self._endpoint = self._get_final_endpoint(endpoint)
        self.app.before_request(self._redirect_slack_requests)
        self._bind_main_entrypoint(endpoint)
        self._bind_events_entrypoint(events_endpoint)

    def _get_final_endpoint(self, endpoint):
        """Prepend blueprint prefix to endpoint if used as a blueprint"""
        if self._is_blueprint() and not self.app.url_prefix:
            # TODO: Perhaps relax this constraint once we figure out how to know
            # at which url_prefix the blueprint will be listening on registration.
            # Probably hooking after Blueprint.register to update with app.bp.url_prefix
            raise ValueError(f"Missing required 'url_prefix' for blueprint {self.app.name}")

        return f'{self.app.url_prefix}{endpoint}' if self._is_blueprint() else endpoint

    def _is_blueprint(self):
        return isinstance(self.app, Blueprint)

    def _bind_main_entrypoint(self, endpoint):
        self.app.add_url_rule(endpoint, 'slackify_entrypoint', lambda: '🚀 Slackify Home', methods=('GET', 'POST'))

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

        view_func = self._get_endpoint_handler(endpoint)
        injected_func = self.injector.inject(view_func)
        return injected_func(**request.view_args)

    def _get_endpoint_handler(self, endpoint):
        endpoint = f'{self.app.name}.{endpoint}' if self._is_blueprint() else endpoint
        view_func = self.app.view_functions[endpoint]
        return view_func

    def _should_handle_request(self, req):
        return req.method == 'POST' and request.path == self._endpoint

    def default(self, func: Callable[[], Response]):
        """Register function to execute when an unknown command is received

        Usage:
            >>> @slackify.default
            >>> def unknown_command():
            ...    return 'Unknown Command'
        """
        self._handle_unknown = func

    def _handle_unknown(self):
        """Ignore unknown commands by default."""
        return None

    def error(self, func: Callable[[Exception], Response]):
        """Register function to execute when an exception was raised on any registered handler

        Usage:
            >>> @slackify.error
            >>> def new_handler(exception):
            ...     return f'Something went wrong! {exception!r}'
        """
        self._handle_error = func

    def _handle_error(self, e):
        return self.app.make_response(('Something went wrong..', 500))

    def shortcut(self, shortcut_id: str, **options):
        """Register a function as a shortcut callback

        Usage:
            >>> @slackify.shortcut('my-shortcut')
            >>> def hello():
            ...     print('Someone followed `my-shortcut`')
        """

        def register_handler(shortcut_handler):
            command = shortcut_id
            self.app.add_url_rule(f'/{command}', command, shortcut_handler, **options)
            self.dispatcher.add_matcher(ShortcutMatcher(command))
            return shortcut_handler

        return register_handler

    def command(self, func=None, **options):
        """Register a function as a command handler.

        It can be used as a plain decorator or as a parametrized decorator factory.

        Usage:
            >>> @slackify.command
            >>> def hola():
            ...     print('hola')

            >>> @slackify.command(name='goodbye')
            >>> def chau():
            ...     print('chau')
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
        """Register a function as an action callback.

        It supports registering actions by just `action_id` and  `action_id` + `block_id`

        Usage:

            >>> @slackify.action('action_id')
            >>> def action_id_callback():
            ...    return 'Hello'
            ...
            >>> @slackify.action(action_id='action_id', block_id='block_id')
            >>> def other_callback():
            ...     return 'Bye'
        """

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
        """Register a function as a view callback.

        Usage:
            >>> @slackify.view('my_view')
            >>> def view_callback():
            ...     return 'Hello'
        """

        def decorate(func):
            self.app.add_url_rule(f'/{view_callback_id}', view_callback_id, func, **options)
            self.dispatcher.add_matcher(ViewMatcher(view_callback_id))
            return func

        return decorate

    def event(self, event: str, func=None):
        """Register a function as an event callback.

        Note:
            All event callbacks *MUST* accept a payload positional argument.
            The event payload from slack will be sent on that arg

        Usage:

            >>> @slackify.event('reaction_added')
            >>> def handle_reaction(payload):
            ...     print(payload)
            ...     return 'Hello'
        """
        def add_listener(func):
            if len(signature(func).parameters) != 1:
                error = f"Invalid signature for '{func.__name__}'. Must expect one and only one positional argument"
                raise TypeError(error)

            self.emitter.on(event, func)

        return add_listener(func) if func else add_listener

    def message(self, message, func=None, **kwargs):
        """Register a function as a callback for when a string matching `message` is found.

        Note:
            The event callback *MUST* accept a payload positional argument.
            The event payload from slack will be sent on that arg

        Usage:

            >>> @slackify.message('hello')
            >>> def handle_reaction(payload):
            ...    return 'How are you?'
            ...
            >>> BYE_REGEX = re.compile(r'bye|goodbye|see you|chau')
            >>> @slackify.message(BYE_REGEX)
            >>> def say_bye(payload):
            ...    return 'Bye!

        """

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
