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

def test_message_pin_server_invalid_token(url):
    """ Test invalid token """
    r = requests.post(f'{url}/message/pin', json={'token': 'not_a_token', 'message_id': 0})
    assert r.status_code == AccessError.code

def test_message_pin_server_message_does_not_exist(url, register_users):
    """ Test InputError for message does not exist """
    (user_1, _, user_3) = register_users
    r1 = requests.post(f'{url}/message/pin', json={'token': user_1['token'], 'message_id': 0})
    r2 = requests.post(f'{url}/message/pin', json={'token': user_3['token'], 'message_id': 0})
    assert r1.status_code == InputError.code
    assert r2.status_code == InputError.code

def test_message_pin_server_not_member_of_channel(url, register_users, create_channels):
    """ Test AccessError for not member of the channel """
    (user_1, _, user_3) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    r1 = requests.post(f'{url}/message/send', json={'token': user_1['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    r2 = requests.post(f'{url}/message/pin', json={'token': user_3['token'], 'message_id': message_id})
    assert r2.status_code == AccessError.code

def test_message_pin_server_not_channel_owner(url, register_users, create_channels):
    """ Test AccessError for when user is not channel owner """
    (_, _, user_3) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    requests.post(f'{url}/channel/join', json={'token': user_3['token'], 'channel_id': pub_c_id_1})
    r1 = requests.post(f'{url}/message/send', json={'token': user_3['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    r2 = requests.post(f'{url}/message/pin', json={'token': user_3['token'], 'message_id': message_id})
    assert r2.status_code == AccessError.code

def test_message_pin_server_message_already_pinned(url, register_users, create_channels):
    """ Test InputError for when message is already pinned """
    (user_1, _, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    r1 = requests.post(f'{url}/message/send', json={'token': user_1['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    requests.post(f'{url}/message/pin', json={'token': user_1['token'], 'message_id': message_id})
    r2 = requests.post(f'{url}/message/pin', json={'token': user_1['token'], 'message_id': message_id})
    assert r2.status_code == InputError.code

def test_message_pin_server_return_type(url, register_users, create_channels):
    """ Test return type for message_pin """
    (user_1, _, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    r1 = requests.post(f'{url}/message/send', json={'token': user_1['token'], 'channel_id': pub_c_id_1, 'message': 'stub1'})
    message_id = (r1.json())['message_id']
    r2 = requests.post(f'{url}/message/pin', json={'token': user_1['token'], 'message_id': message_id})
    assert r2.json() == {}