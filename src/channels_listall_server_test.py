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

def test_channels_listall_server_invalid_token(url):
    """ Test parsing invalid token to function """
    r = requests.get(f'{url}/channels/listall', params={'token': 'not_a_token'})
    assert r.status_code == AccessError.code

def test_channels_listall_server_empty_channel_return(url, register_users):
    """ Test return value when there are no channels """
    (user_1, _, _) = register_users
    r = requests.get(f'{url}/channels/listall', params={'token': user_1['token']})
    channels_dict = r.json()
    assert channels_dict == {'channels':[]}

def test_channels_listall_server_return_type(url, register_users):
    """ Test fields are correct inside the returned channel dictionary """
    (user_1, _, _) = register_users
    requests.post(f'{url}/channels/create', json={
        'token': user_1['token'], 'name': 'some_name', 'is_public': True,
    })
    r = requests.get(f'{url}/channels/listall', params={'token': user_1['token']})
    channels_dict = r.json()
    assert 'channel_id' in channels_dict['channels'][0]
    assert ('name', 'some_name') in channels_dict['channels'][0].items()

def test_channels_listall_server_return_type_multiple(url, register_users):
    """ Test all channels are being returned """
    (user_1, _, _) = register_users
    requests.post(f'{url}/channels/create', json={
        'token': user_1['token'], 'name': 'some_name1', 'is_public': True,
    })
    requests.post(f'{url}/channels/create', json={
        'token': user_1['token'], 'name': 'some_name2', 'is_public': True,
    })
    r = requests.get(f'{url}/channels/listall', params={'token': user_1['token']})
    channels_dict = r.json()
    channel_name_list = [channel['name'] for channel in channels_dict['channels']]
    assert 'some_name1' in channel_name_list
    assert 'some_name2' in channel_name_list
    assert len(channel_name_list) == 2


    
