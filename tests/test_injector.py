import pytest
from slackify.injector import Injector

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

    injected = injector.inject2(func)
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

    injected = injector.inject2(func)
    assert injected is not func
    assert injected('Z') == ('A', 'Z')


def test_injector_two_args(injector):
    def func(a, b):
        return a, b

    injected = injector.inject2(func)
    assert injected is not func
    assert injected() == ('A', 'B')


def test_inject_one_arg(injector):
    def func(a):
        return a

    injected = injector.inject2(func)
    assert injected is not func
    assert injected() == ('A')


def test_inject_all_args(injector):
    def func(a, b, c, d):
        return a, b, c, d

    injected = injector.inject2(func)
    assert injected is not func
    assert injected() == ('A', 'B', 'C', 'D')


def test_injected_args_must_be_the_first_args_or_bad_things_may_happen(injector):
    def func(a, not_injected, b):
        return a, not_injected, b

    injected = injector.inject2(func)
    assert injected('hello') != ('A', 'hello', 'B')
    assert injected('hello') == ('A', 'B', 'hello')

    def func(a, b, not_injected):
        return a, b, not_injected

    injected = injector.inject2(func)
    assert injected('hello') == ('A', 'B', 'hello')
