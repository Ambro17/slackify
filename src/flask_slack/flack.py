import logging

from flask import Flask, request, _request_ctx_stack

from .dispatcher import Dispatcher, ShortcutMatcher, Command, ActionMatcher
from flask_slack.dispatcher import ViewMatcher


logger = logging.getLogger(__name__)


class Flack(Flask):

    def __init__(self, import_name, **kwargs):
        self.dispatcher = Dispatcher()
        super().__init__(import_name, **kwargs)
        self.before_request_funcs.setdefault(None, []).append(self._redirect_requests)
        self.add_url_rule('/', '_entrypoint', lambda: 'Home', methods=('GET', 'POST'))

    def shortcut(self, callback_id, **options):
        def decorate(f):
            command = callback_id
            self.add_url_rule(f'/{command}', command, f, **options)
            self.dispatcher.add_matcher(ShortcutMatcher(command))
            return f

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
        def decorate(f):
            command = options.pop('name', f.__name__)
            rule = f'/{command}' if not command.startswith('/') else command
            self.add_url_rule(rule, command, f, **options)
            self.dispatcher.add_matcher(Command(command))
            return f

        used_as_plain_decorator = bool(func)
        if used_as_plain_decorator:
            return decorate(func)
        else:
            return decorate

    def action(self, id=None, **options):
        if id is None and 'action_id' not in options:
            raise TypeError("action() missing 1 required keyword argument: 'id'")

        def decorate(f):
            command = id or options.pop('action_id')  # TODO: Handle special characters that make url rule invalid?
            block_id = options.pop('block_id', None)
            self.add_url_rule(f'/{command}', command, f, **options)
            self.dispatcher.add_matcher(ActionMatcher(command, block_id=block_id))
            return f

        return decorate

    def view(self, view_callback_id, **options):
        def decorate(f):
            self.add_url_rule(f'/{view_callback_id}', view_callback_id, f, **options)
            self.dispatcher.add_matcher(ViewMatcher(view_callback_id))
            return f

        return decorate

    def event(self, event, **kwargs):
        pass

    def default(self, f):
        self._handle_unknown = f

    def _handle_unknown(self):
        """Ignore unknown commands by default."""
        return None

    def error(self, f):
        self._handle_error = f

    def _handle_error(self, e):
        return 'Oops..'

    def _redirect_requests(self):
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)

        if request.method == 'GET':
            return

        try:
            endpoint = self.dispatcher.match(req)
        except StopIteration:
            logger.info('No handler matched this request')
            return self._handle_unknown()
        except Exception as e:
            logger.exception('Something bad happened.')
            return self._handle_error(e)

        rule = req.url_rule
        rule.endpoint = endpoint
