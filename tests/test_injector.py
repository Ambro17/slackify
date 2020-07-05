from flask.blueprints import Blueprint
from build.lib import slackify
from tests.conftest import bare_app, bare_client
from flask import Flask
import pytest

from slackify import Slackify
from slackify.injection import Injector


@pytest.fixture(scope='module')
def injector():
    return Injector(
        {
            'a': lambda: 'A',
            'b': lambda: 'B',
            'c': lambda: 'C',
            'd': lambda: 'D',
        }
    )


def test_injector_no_dependencies_injected_returns_function_unmodified(injector):
    def func(arg):
        pass

    injected = injector.inject(func)
    assert injected is func


def test_injector_one_arg_as_kwarg(injector):
    def func(a, z):
        return a, z

    injected = injector.inject(func)
    assert injected is not func
    assert injected(z='Z') == ('A', 'Z')


def test_injector_one_arg_as_positional(injector):
    def func(a, z):
        return a, z

    injected = injector.inject(func)
    assert injected is not func
    assert injected('Z') == ('A', 'Z')


def test_injector_two_args(injector):
    def func(a, b):
        return a, b

    injected = injector.inject(func)
    assert injected is not func
    assert injected() == ('A', 'B')


def test_inject_one_arg(injector):
    def func(a):
        return a

    injected = injector.inject(func)
    assert injected is not func
    assert injected() == ('A')


def test_inject_all_args(injector):
    def func(a, b, c, d):
        return a, b, c, d

    injected = injector.inject(func)
    assert injected is not func
    assert injected() == ('A', 'B', 'C', 'D')


def test_injected_args_must_be_the_first_args_or_bad_things_may_happen(injector):
    def func(a, not_injected, b):
        return a, not_injected, b

    injected = injector.inject(func)
    assert injected('hello') != ('A', 'hello', 'B')
    assert injected('hello') == ('A', 'B', 'hello')

    def func2(a, b, not_injected):
        return a, b, not_injected

    injected = injector.inject(func2)
    assert injected('hello') == ('A', 'B', 'hello')


def test_injector_with_real_app(bare_app, bare_client):
    slackify = bare_app
    client = bare_client

    @slackify.command
    def hello(command):
        return f'I am {command}'

    rv = client.post('/',
                     data={'command': '/hello'},
                     content_type='application/x-www-form-urlencoded')
    assert b'I am /hello' == rv.data


def test_injector_with_blueprint():
    bp = Blueprint('TestBlueprint', __name__, url_prefix='/bp_url_prefix')
    slackify = Slackify(app=bp, endpoint='/slack')

    @slackify.command
    def greeting(command):
        return f'I am {command}'

    app = Flask('Bare')
    app.register_blueprint(bp)
 
    import pdb; pdb.set_trace()
    with app.test_client() as client:
        rv = client.post('/bp_url_prefix/slack',
                        data={'command': '/greeting'},
                        content_type='application/x-www-form-urlencoded')
        assert b'I am /greeting' == rv.data, rv.data

# TypeError: hello() missing 1 required positional argument: 'command'
# Flask routing should be overriden to allow extra args that were unknown on registration.