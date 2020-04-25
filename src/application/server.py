from flask import Flask, request, _request_ctx_stack
from .dispatcher import dp, ShortcutMatcher, Command, ActionMatcher


class Flack(Flask):

    def __init__(self, import_name, **kwargs):
        self.dispatcher = kwargs.pop('dispatcher')
        super().__init__(import_name, **kwargs)

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

    def action(self, **action_filter):
        if 'action_id' not in action_filter:
            raise TypeError("action() missing 1 required keyword argument: 'action_id'")

        def decorate(f):
            command = action_filter.pop('action_id')  # TODO: Handle special characters that make url rule invalid?
            self.add_url_rule(f'/{command}', command, f, **action_filter)
            self.dispatcher.add_matcher(ActionMatcher(command, **action_filter))
            return f

        return decorate


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
        endpoint = 'error'


    rule = req.url_rule
    rule.endpoint = endpoint


@app.route('/', methods=('GET', 'POST'))
def home():
    return 'Home'


@app.command(name='chau')
def hello():
    return 'Hello'


@app.shortcut('my-shortcut')
def shortcut():
    return 'Shortcut'


@app.route('/unknown')
def unknown():
    return 'Unknown Command'


@app.route('/error')
def error():
    return "Oops.. I really didn't really expect this"