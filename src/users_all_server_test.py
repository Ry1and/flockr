# -------------------------- Tests for users/all route -------------------------

# pytest.fixture and test_url copied from the provided file echo_http_test.py

import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users

# Tests for error when given an invalid token.
def test_users_all_invalid_token(url, register_users):
    register_users

    invalid_token = 'invalidtoken'
    all = requests.get(f"{url}/users/all?token={invalid_token}")

    assert all.status_code == AccessError.code

# Tests for success when a global owner gets user details.
def test_users_all_global_owner(url, register_users):
    (user_1, _, _) = register_users

    all = requests.get(f"{url}/users/all?token={user_1['token']}")

    payload = all.json()
    assert len(payload) == 1
    assert len(payload['users']) == 3
    assert payload['users'][0]['u_id'] == 1
    assert payload['users'][0]['email'] == 'user1@gmail.com'
    assert payload['users'][0]['name_first'] == 'name_1'
    assert payload['users'][0]['name_last'] == 'surname_1'
    assert payload['users'][0]['handle_str'] == 'name_1surname_1'
    
    assert payload['users'][2]['u_id'] == 3
    assert payload['users'][2]['email'] == 'user3@gmail.com'
    assert payload['users'][2]['name_first'] == 'name_3'
    assert payload['users'][2]['name_last'] == 'surname_3'
    assert payload['users'][2]['handle_str'] == 'name_3surname_3'

# Tests for success when a global member gets user details.
def test_users_all_global_member(url, register_users):
    (_, user_2, _) = register_users

    all = requests.get(f"{url}/users/all?token={user_2['token']}")

    payload = all.json()

    assert len(payload) == 1
    assert len(payload['users']) == 3
    assert payload['users'][0]['u_id'] == 1
    assert payload['users'][0]['email'] == 'user1@gmail.com'
    assert payload['users'][0]['name_first'] == 'name_1'
    assert payload['users'][0]['name_last'] == 'surname_1'
    assert payload['users'][0]['handle_str'] == 'name_1surname_1'
    
    assert payload['users'][1]['u_id'] == 2
    assert payload['users'][1]['email'] == 'user2@gmail.com'
    assert payload['users'][1]['name_first'] == 'name_2'
    assert payload['users'][1]['name_last'] == 'surname_2'
    assert payload['users'][1]['handle_str'] == 'name_2surname_2'
