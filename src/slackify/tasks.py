from functools import wraps
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

pool = ThreadPoolExecutor(max_workers=10)


def async_task(callable: Callable):
    """Run a `Callable` in a background thread so it doesn't block main thread

    This decorator might be useful if you want to avoid getting slack timeout
    because your handlers are taking more than 3 seconds to respond.
    See `examples.async_task` for usage details
    """

    @wraps(callable)
    def wrapper(*args, **kwargs):
        future = pool.submit(callable, *args, **kwargs)
        return future

    return wrapper
