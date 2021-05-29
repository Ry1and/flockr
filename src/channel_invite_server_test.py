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

def test_channel_invite_invalid_channel(url, register_users, create_channels):
    '''
    Tests for error when inviting a member to an invalid channel.
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, priv_c_id_1, pub_c_id_2, priv_c_id_2) = create_channels
    invalid_id = pub_c_id_1 + priv_c_id_1 + pub_c_id_2 + priv_c_id_2

    invite = requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': invalid_id, 'u_id': user_2['u_id']})

    assert invite.status_code == InputError.code

def test_channel_invite_invalid_user(url, register_users, create_channels):
    '''
    Tests for error when inviting an invalid user to a channel.
    '''

    (user_1, user_2, user_3) = register_users
    (_, priv_c_id_1, _, _) = create_channels
    invalid_u_id = user_1['u_id'] + user_2['u_id'] + user_3['u_id'] 

    invite = requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': priv_c_id_1, 'u_id': invalid_u_id})

    assert invite.status_code == InputError.code

def test_channel_invite_invalid_token(url, register_users, create_channels):
    '''
    Tests for error when an invalid token is given.
    '''

    (user_1, _, _) = register_users
    (_, priv_c_id_1, _, _) = create_channels

    invalid_token = 'invalidtoken'

    invite = requests.post(f"{url}/channel/invite", json={'token': invalid_token,
    'channel_id': priv_c_id_1, 'u_id': user_1['u_id']})

    assert invite.status_code == AccessError.code 

def test_channel_invite_non_member_others(url, register_users, create_channels):
    '''
    Tests for error when non-member invites another member to a channel.
    '''

    (user_1, _, user_3) = register_users
    (_, _, pub_c_id_2, _) = create_channels

    invite = requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': pub_c_id_2, 'u_id': user_3['u_id']
    })

    assert invite.status_code == AccessError.code

def test_channel_invite_non_member_self(url, register_users, create_channels):
    '''
    Tests for error when non-member invites themselves to a channel.
    '''

    (user_1, _, _) = register_users
    (_, _, _, priv_c_id_2) = create_channels

    invite = requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': priv_c_id_2, 'u_id': user_1['u_id']
    })

    assert invite.status_code == AccessError.code

def test_channel_invite_owner_member(url, register_users, create_channels):
    '''
    Tests for success when an owner invites another global member to a channel.
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    t_2 = user_2['token']

    requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': pub_c_id_1, 'u_id': user_2['u_id']
    })

    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={pub_c_id_1}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 2
    assert payload['all_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)
    assert payload['all_members'][1]['u_id'] == user_2['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_2'
    assert payload['all_members'][1]['name_last'] == 'surname_2' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)

def test_channel_invite_member_member(url, register_users, create_channels):
    '''
    Tests for success when a member invites another global member to a channel.
    '''

    (user_1, user_2, user_3) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    t_2 = user_2['token']

    requests.post(f"{url}/channel/join", json={'token': user_3['token'],
    'channel_id': pub_c_id_1})

    requests.post(f"{url}/channel/invite", json={'token': user_3['token'],
    'channel_id': pub_c_id_1, 'u_id': user_2['u_id']
    })

    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={pub_c_id_1}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 3
    assert payload['all_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)
    assert payload['all_members'][1]['u_id'] == user_3['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_3'
    assert payload['all_members'][1]['name_last'] == 'surname_3' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)
    assert payload['all_members'][2]['u_id'] == user_2['u_id'] 
    assert payload['all_members'][2]['name_first'] == 'name_2'
    assert payload['all_members'][2]['name_last'] == 'surname_2' 
    assert payload['all_members'][2]['profile_img_url'].startswith(url)

def test_channel_invite_member_self(url, register_users, create_channels):
    '''
    Tests for no effect when a member invites themselves to a channel. 
    '''
    
    (user_1, _, _) = register_users
    (_, priv_c_id_1, _, _) = create_channels
    t_1 = user_1['token']

    requests.post(f"{url}/channel/invite", json={'token': user_1['token'],
    'channel_id': priv_c_id_1, 'u_id': user_1['u_id']
    })

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={priv_c_id_1}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert len(payload['all_members']) == 1

def test_channel_invite_member_within_channel(url, register_users, create_channels):
    '''
    Tests for no effect when a member invites another member to a channel. 
    '''

    (user_1, user_2, user_3) = register_users
    (pub_c_id_1, _, _, _) = create_channels
    t_2 = user_2['token']   

    requests.post(f"{url}/channel/join", json={'token': user_3['token'],
    'channel_id': pub_c_id_1})

    requests.post(f"{url}/channel/invite", json={'token': user_3['token'],
    'channel_id': pub_c_id_1, 'u_id': user_2['u_id']
    })

    requests.post(f"{url}/channel/invite", json={'token': user_3['token'],
    'channel_id': pub_c_id_1, 'u_id': user_2['u_id']
    })

    requests.post(f"{url}/channel/invite", json={'token': user_3['token'],
    'channel_id': pub_c_id_1, 'u_id': user_2['u_id']
    })

    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={pub_c_id_1}")

    payload = details.json()
    
    assert len(payload['owner_members']) == 1
    assert payload['all_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 3
    assert payload['all_members'][2]['u_id'] == user_2['u_id'] 
    assert payload['all_members'][2]['name_first'] == 'name_2'
    assert payload['all_members'][2]['name_last'] == 'surname_2' 
    assert payload['all_members'][2]['profile_img_url'].startswith(url)
    