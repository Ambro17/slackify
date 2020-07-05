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

        injected_args = {
            param: self.injectors[param]()
            for param in params_to_inject
        }
        if injected_args:
            fn = functools.partial(fn, **injected_args)

        return fn

    def inject2(self, fn: Callable) -> Callable:
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



def get_payload():
    return json.loads(request.form["payload"])

def get_command_args():
    return request.form["text"]

def get_command():
    return request.form["command"]

def get_response_url():
    return request.form["response_url"]
    
def get_shortcut():
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
