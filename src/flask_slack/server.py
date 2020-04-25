import logging
from flask import Flask, request, _request_ctx_stack
from .dispatcher import dp, ShortcutMatcher, Command, ActionMatcher
from slack import WebClient

cli = WebClient('xoxb-SECRET')


logging.basicConfig()
logger = logging.getLogger(__name__)


class Flack(Flask):

    def __init__(self, import_name, **kwargs):
        if 'dispatcher' not in kwargs:
            raise ValueError('Missing required dispatcher argument')
        self.dispatcher = kwargs.pop('dispatcher')
        super().__init__(import_name, **kwargs)
        self.before_request_funcs.setdefault(None, []).append(self._redirect_requests)
        self.add_url_rule('/', 'home', lambda: 'Home', methods=('GET', 'POST'))

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

        options['methods'] = ('GET', 'POST')

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
            options['methods'] = ('GET', 'POST')
            self.add_url_rule(f'/{command}', command, f, **options)
            self.dispatcher.add_matcher(ActionMatcher(command, **options))
            return f

        return decorate

    def _redirect_requests(self):
        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            app.raise_routing_exception(req)

        if request.method == 'GET':
            return

        try:
            endpoint = app.dispatcher.match(req)
        except StopIteration:
            endpoint = 'unknown'
        except Exception:
            logger.exception('Bad')
            endpoint = 'error'

        rule = req.url_rule
        rule.endpoint = endpoint


app = Flack(__name__, dispatcher=dp)


@app.before_request
def redirect_requests():
    req = _request_ctx_stack.top.request
    if req.routing_exception is not None:
        app.raise_routing_exception(req)

    if request.method == 'GET':
        return

    try:
        endpoint = app.dispatcher.match(req)
    except StopIteration:
        endpoint = 'unknown'
    except Exception as e:
        print(repr(e))
        endpoint = 'error'

    rule = req.url_rule
    rule.endpoint = endpoint


@app.command(name='chau')
def hello():
    return 'Hello'


@app.shortcut('funny_joke')
def shortcut():
    cli.chat_postMessage(channel='#general', text='Hi!')
    return 'Shortcut'


@app.action(id='my-action-id')
def my_action():
    return 'Action'


@app.route('/unknown')
def unknown():
    return 'Unknown Command'


@app.route('/error')
def error():
    return "Oops.. I really didn't really expect this"
