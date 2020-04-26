import json


def test_home_page(client):
    rv = client.get('/')
    assert b'Home' in rv.data


def test_redirect_to_command_handler(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/chau'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Hello' in rv.data


def test_function_name_gets_overriden_by_decorator_arg(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/hello'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Unknown Command' in rv.data


def test_redirect_to_command_handler_fails_on_invalid_command(client):
    """Redirect to /hello based on form command"""
    rv = client.post('/',
                     data={'command': '/Inexistent'},
                     content_type='application/x-www-form-urlencoded')
    assert b'Unknown Command' in rv.data


def test_redirect_to_shortcut_handler(client):
    args = {
        'payload': json.dumps({
            'type': 'shortcut',
            'callback_id': 'my-shortcut'
        })
    }
    rv = client.post('/',
                     data=args,
                     content_type='application/x-www-form-urlencoded')
    assert b'Shortcut' in rv.data


def test_redirect_to_shortcut_handler_invalid_id(client):
    args = {
        'payload': {
            'type': 'shortcut',
            'callback_id': 'not-a-shortcut'
        }
    }
    rv = client.post('/', json=args)
    assert b'Unknown Command' in rv.data


def test_if_exception_is_raised_request_is_redirect_to_error_handler(client):
    args = {
        'payload': "Breaking JSON"
    }
    rv = client.post('/',
                     data=args,
                     content_type='application/x-www-form-urlencoded')
    assert b'Oops..' in rv.data


def test_request_handling_with_no_added_matchers():
    pass


def test_redirect_on_action_id(client):
    payload = {
        "type": "block_actions",
        "actions": [{
            'action_id': 'my-action-id',
            'block_id': 'block-id',
        }],
        "token": "",
        "response_url": "",
        "trigger_id": "",
    }
    rv = client.post('/',
                     data={'payload': json.dumps(payload)},
                     content_type='application/x-www-form-urlencoded')

    assert b'Action' == rv.data
