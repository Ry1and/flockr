# ----------------------- Tests for channel/details route ----------------------

# pytest.fixture copied from the provided file echo_http_test.py

import pytest
from flask import request
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels

def test_channel_details_no_channels(url, register_users, create_channels):
    '''
    Tests for error when getting details for an invalid channel.
    '''

    (user_1, _, _) = register_users
    (pub_c_id_1, priv_c_id_1, pub_c_id_2, priv_c_id_2) = create_channels
    t_1 = user_1['token']
    inv_c_id = pub_c_id_1 + priv_c_id_1 + pub_c_id_2 + priv_c_id_2

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={inv_c_id}")

    assert details.status_code == InputError.code

def test_channel_details_non_member(url, register_users, create_channels):
    '''
    Tests for error when an unauthorised member gets details for a channel.
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, priv_c_id_2) = create_channels
    t_1 = user_1['token']
    t_2 = user_2['token']

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={priv_c_id_2}")

    assert details.status_code == AccessError.code

    details = requests.get(f"{url}/channel/details?token={t_2}&channel_id={pub_c_id_1}")

    assert details.status_code == AccessError.code

def test_channel_details_invalid_token(url, register_users, create_channels):
    '''
    Tests for error when an invalid token is given.
    '''

    register_users
    (pub_c_id_1, _, _, _) = create_channels

    inv_token = 'invalidtoken'

    details = requests.get(f"{url}/channel/details?token={inv_token}&channel_id={pub_c_id_1}")

    assert details.status_code == AccessError.code

def test_channel_details_success_owner(url, register_users, create_channels):
    '''
    Tests for success when an owner of a channel gets details for the channel.
    '''

    (user_1, _, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels    
    t_1 = user_1['token']
    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={pub_c_id_1}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 1
    assert payload['all_members'][0]['u_id'] == user_1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)
    

def test_channel_details_success_member(url, register_users, create_channels):
    '''
    Tests for success when a member of a channel gets details for the channel.
    '''

    (user_1, user_2, _) = register_users
    (pub_c_id_1, _, _, _) = create_channels    
    t_2 = user_2['token']

    requests.post(f"{url}/channel/join", json={'token': user_2['token'],
    'channel_id': pub_c_id_1})

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
