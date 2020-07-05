import functools
import inspect
import json
from typing import Callable, Mapping

from flask import request


class Injector:
    """Inject dependencies into functions to avoid repetitive request parsing"""

    def __init__(self, injectors: Mapping[str, Callable]):
        self.injectors = injectors

    def inject(self, fn: Callable) -> Callable:
        """Inject parameters declared as function dependencies and return the injected function
        
        Note: 
            Functions should be injected *at call time*, rather than function definition time, 
            as injectors might need flask request context that's only available at call timec
        """
        parameters = inspect.signature(fn).parameters
        params_to_inject = [p for p in parameters if p in self.injectors]

        for param in params_to_inject:
            inject_param = self.injectors[param]
            fn = functools.partial(fn, inject_param())

        return fn

    def __repr__(self) -> str:
        return f'{type(self).__name__}(injectors={self.injectors})'


def get_payload() -> dict:
    """Interactive actions have form content type, but contain json inside the payload key"""
    return json.loads(request.form["payload"])

def get_command_args() -> str:
    return request.form["text"]

def get_command() -> str:
    return request.form["command"]

def get_response_url() -> str:
    return request.form["response_url"]
    
def get_shortcut() -> dict:
    """Global and message shortcuts have json content type"""
    return request.get_json()['payload']


injector = Injector(
    injectors={
        'payload': get_payload,
        'command': get_command,
        'command_args': get_command_args,
        'response_url': get_response_url,
        'shortcut': get_shortcut,
    }
)
