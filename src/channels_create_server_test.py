import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from server_test_fixtures import url, register_users
from error import AccessError, InputError

@pytest.fixture(autouse=True)
def clear_only(url):
    requests.delete(f'{url}/clear')

def test_channels_create_server_invalid_token(url):
    ''' Checks AccessError is raised correctly when invalid token is given '''
    r = requests.post(f'{url}/channels/create', json={
        'token': 'not_a_token', 
        'name': 'some_name', 
        'is_public': True,
    })
    assert r.status_code == AccessError.code

def test_channels_create_server_name_longer_than_20(url, register_users):
    ''' Checks InputError is raised correctly when name is too long '''
    (user_1, _, _) = register_users
    r = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'], 
        'name': 'superduperlongnames21', 
        'is_public': True,
    })
    assert r.status_code == InputError.code

def test_channels_create_server_return_type(url, register_users):
    ''' Checks channels_create return type is of {'channel_id': <channel_id>} '''
    (user_1, _, _) = register_users
    r = requests.post(f'{url}/channels/create', json={
        'token': user_1['token'], 
        'name': 'some_name', 
        'is_public': True,
    })
    payload = r.json()
    assert 'channel_id' in payload.keys()
    assert len(payload) == 1
