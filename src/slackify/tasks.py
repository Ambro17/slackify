from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(max_workers=10)


def async_task(f):
    def wrapper(*args, **kwargs):
        future = pool.submit(f, *args, **kwargs)
        return future
    return wrapper
