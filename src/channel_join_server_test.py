# ------------------------ Tests for channel/join route ------------------------

# pytest.fixture copied from the provided file echo_http_test.py

import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels

def test_channel_join_invalid_token(url, register_users, create_channels):
    '''
    Tests for error when an invalid token is given. 
    '''

    register_users
    (pub_c_id_1, _, _, priv_c_id_2) = create_channels
    
    invalid_token = 'invalidtoken'

    join = requests.post(f"{url}/channel/join", json={'token': invalid_token,
    'channel_id': pub_c_id_1})    

    assert join.status_code == AccessError.code

    join = requests.post(f"{url}/channel/join", json={'token': invalid_token,
    'channel_id': priv_c_id_2})    

    assert join.status_code == AccessError.code

def test_channel_join_invalid_channel(url, register_users, create_channels):
    '''
    Tests for error when joining an invalid channel.
    '''

    (user_1, _, _) = register_users
    (pub_c_id_1, priv_c_id_1, pub_c_id_2, priv_c_id_2) = create_channels
    invalid_id = pub_c_id_1 + priv_c_id_1 + pub_c_id_2 + priv_c_id_2

    join = requests.post(f"{url}/channel/join", json={'token': user_1['token'],
    'channel_id': invalid_id})

    assert join.status_code == InputError.code

def test_channel_join_private_channel(url, register_users, create_channels):
    '''
    Tests for error when a member joins a private channel.
    '''

    (_, user_2, _) = register_users
    (_, priv_c_id_1, _, _) = create_channels

    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': priv_c_id_1})

    assert join.status_code == AccessError.code 

def test_channel_join_global_owner(url, register_users, create_channels):
    '''
    Tests for success when a global owner joins a private channel. 
    '''

    (user_1, user_2, _) = register_users
    (_, _, _, priv_c_id_2) = create_channels
    t_2 = user_2['token']

    join = requests.post(f"{url}/channel/join", json={'token': user_1['token'],
    'channel_id': priv_c_id_2})

    payload = join.json()
    assert payload == {}

    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={priv_c_id_2}")
    
    payload = details.json()

    assert len(payload['owner_members']) == 2
    assert payload['owner_members'][0]['name_first'] == 'name_2'
    assert payload['owner_members'][0]['name_last'] == 'surname_2' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)
    
    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_1'
    assert payload['all_members'][1]['name_last'] == 'surname_1' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)

def test_channel_join_pub_channel_owner(url, register_users, create_channels):
    '''
    Tests for success when a global owner joins a public channel. 
    '''

    (user_1, user_2, _) = register_users
    (_, _, pub_c_id_2, _) = create_channels
    t_2 = user_2['token']

    join = requests.post(f"{url}/channel/join", json={
        'token': user_1['token'],
        'channel_id': pub_c_id_2
    })

    payload = join.json()
    assert payload == {}
    
    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={pub_c_id_2}")
    
    payload = details.json()
    
    assert len(payload['owner_members']) == 2
    assert payload['owner_members'][0]['name_first'] == 'name_2'
    assert payload['owner_members'][0]['name_last'] == 'surname_2' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)
    
    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_1'
    assert payload['all_members'][1]['name_last'] == 'surname_1' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)

def test_channel_join_member(url, register_users, create_channels):
    '''
    Tests for success when a member joins a public channel. 
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    t_1 = user_1['token']

    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})
    
    payload = join.json()
    assert payload == {}

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={pub_c_id_1}")
    
    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user_2['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_2'
    assert payload['all_members'][1]['name_last'] == 'surname_2' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)

def test_channel_join_multiple_times(url, register_users, create_channels):
    '''
    Tests for no effect when a member (re-)joins a channel. 
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    t_1 = user_1['token']

    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})
    
    payload = join.json()
    assert payload == {}

    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})
    
    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})
    
    join = requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={pub_c_id_1}")
    
    payload = details.json()
    
    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user_2['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_2'
    assert payload['all_members'][1]['name_last'] == 'surname_2' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)
