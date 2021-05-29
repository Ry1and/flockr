import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from server_test_fixtures import url, register_users, create_channels
from error import AccessError, InputError

@pytest.fixture(autouse=True)
def clear_only(url):
    requests.delete(f'{url}/clear')

def test_message_remove_server_invalid_token(url):
    """ Test invalid token """
    r = requests.delete(f'{url}/message/remove', json={'token': 'not_a_token', 'message_id': 0})
    assert r.status_code == AccessError.code

def test_message_remove_server_not_authorised_not_owner(url, register_users, create_channels):
    """
    Test case for user not a global owner, not a channel owner, not the user
    that sent the message.
    """
    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    r1 = requests.post(f'{url}/message/send', json={'token': user_1['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    r2 = requests.delete(f'{url}/message/remove', json={'token': user_2['token'], 'message_id': message_id})
    assert r2.status_code == AccessError.code

def test_message_remove_server_message_does_not_exist(url, register_users):
    """ Test for message does not exist """
    (user_1, _, _) = register_users
    r = requests.delete(f'{url}/message/remove', json={'token': user_1['token'], 'message_id': 0})
    assert r.status_code == InputError.code

def test_message_remove_server_message_exists(url, register_users, create_channels):
    """ Test for message that does exist """
    (user_1, _, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    r1 = requests.post(f'{url}/message/send', json={'token': user_1['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    r2 = requests.delete(f'{url}/message/remove', json={'token': user_1['token'], 'message_id': message_id})
    assert r2.json() == {}
