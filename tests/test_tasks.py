from slackify import async_task, respond
from unittest.mock import patch


def test_async_task_decorator():
    @async_task
    def delayed_func():
        return 17

    future = delayed_func()
    assert future.result(timeout=5) == 17


def test_respond_call_is_async():
    with patch('requests.post') as mock_request:
        mock_request.return_value = 1
        future = respond('https://url.com', 'message')
        assert future.result(timeout=5) == 1
