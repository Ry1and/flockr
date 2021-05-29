import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels

def test_sanity(url):
    '''Test to check if the server is running '''
    assert url.startswith("http")


def test_invalid_channel(url, register_users):
    '''When the channel_id is invalid, raise an input error'''
    (user1, _, _) = register_users
    leave = requests.post(f"{url}/channel/leave",json={'token': user1['token'],'channel_id': -42})
    
    assert leave.status_code == InputError.code

def test_invalid_token(url, create_channels):
    '''When the token is invalid, raise an  Input error, for a public and a private channel'''
    (pub_channel, priv_channel, _, _) = create_channels

    # joining a public channel with an invalid token
    leave = requests.post(f"{url}/channel/leave",json={'token': 'invalidtoken','channel_id': pub_channel})
    assert leave.status_code == AccessError.code

    # joining a private channel with an invalid toke
    leave = requests.post(f"{url}/channel/leave",json={'token': 'invalidtoken','channel_id': priv_channel})
    assert leave.status_code == AccessError.code


def test_not_member_public(url, register_users, create_channels):
    '''raise an access error when the user is not a member of a public channel'''
    
    (_, _, user3) = register_users
    
    #user 1 creates a public channel
    (pub_channel, _, _, _) = create_channels

    #user 3 tries to leave pub_channel
    leave = requests.post(f"{url}/channel/leave",json={'token': user3['token'],'channel_id': pub_channel})
    assert leave.status_code == AccessError.code


def test_not_member_private(url, register_users, create_channels):
    (_, _, user3) = register_users

    (_, priv_channel, _, _) = create_channels

    leave = requests.post(f"{url}/channel/leave", json={'token': user3['token'],'channel_id': priv_channel})
    assert leave.status_code == AccessError.code


def test_public_member_leave(url, register_users):
    ''' The member of a public channel leaves the channel'''

    (user1, user2, user3) = register_users

    #user 1 creates a public channel
    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': True
        }).json())['channel_id']

    #user3 and user2 join pub_channel as a member
    requests.post(f"{url}/channel/join", json={'token': user3['token'], 'channel_id' : c_id})
    requests.post(f"{url}/channel/join", json={'token' : user2['token'], 'channel_id' : c_id})

    # user3 leaves the channel
    leave = requests.post(f"{url}/channel/leave", json={'token' : user3['token'], 'channel_id' : c_id})
    payload = leave.json()

    assert payload == {}

    # check if user3 is no longer a member if pub_channel
    details = requests.get(f"{url}/channel/details?token={user2['token']}&channel_id={c_id}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user2['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_2'
    assert payload['all_members'][1]['name_last'] == 'surname_2' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)


def test_private_member_leave(url, register_users):
    '''The member of a private channel leaves the channel '''
    
    (user1, user2, user3) = register_users

    #user 1 creates a private channel
    c_name = "private_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': False
        }).json())['channel_id']
    

    #user3 and user2 join pub_channel as a member
    requests.post(f"{url}/channel/invite", json={'token': user1['token'], 'u_id' : user2['u_id'], 'channel_id' : c_id})
    requests.post(f"{url}/channel/invite", json={'token' : user1['token'], 'u_id' : user3['u_id'], 'channel_id' : c_id})

    # user3 leaves the channel
    requests.post(f"{url}/channel/leave", json={'token' : user3['token'], 'channel_id' : c_id})

    # check if user3 is no longer a member if pub_channel
    details = requests.get(f"{url}/channel/details?token={user2['token']}&channel_id={c_id}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 2
    assert payload['all_members'][1]['u_id'] == user2['u_id'] 
    assert payload['all_members'][1]['name_first'] == 'name_2'
    assert payload['all_members'][1]['name_last'] == 'surname_2' 
    assert payload['all_members'][1]['profile_img_url'].startswith(url)


def test_leave_public_owner(url, register_users):
    '''When an owner of a public channel leaves'''
     
    (user1, user2, _) = register_users

    #user 1 creates a public channel
    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': True
        }).json())['channel_id']


    # promote user2 to channel owner for public channel
    requests.post(f"{url}/channel/addowner", json={
        'token': user1['token'],
        'channel_id' : c_id, 
        'u_id' : user2['u_id']}
        )
    
    # user2 leaves the channel
    requests.post(f"{url}/channel/leave", json={'token' : user2['token'], 'channel_id' : c_id})
    
    details = requests.get(f"{url}/channel/details?token={user1['token']}&channel_id={c_id}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 1
    assert payload['all_members'][0]['u_id'] == user1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)


def test_leave_private_owner(url, register_users):
    '''When the owner of a private channel leaves the channel'''
    (user1, user2, _) = register_users

    #user 1 creates a private channel
    c_name = "private_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': False
        }).json())['channel_id']


    # user1 adds user2 as an owner of the channel
    requests.post(f"{url}/channel/addowner", json={
        'token': user1['token'],
        'channel_id' : c_id, 
        'u_id' : user2['u_id']}
        )
    
    # user2 leaves the channel
    requests.post(f"{url}/channel/leave", json={'token' : user2['token'], 'channel_id' : c_id})
    
    details = requests.get(f"{url}/channel/details?token={user1['token']}&channel_id={c_id}")

    payload = details.json()

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user1['u_id'] 
    assert payload['owner_members'][0]['name_first'] == 'name_1'
    assert payload['owner_members'][0]['name_last'] == 'surname_1' 
    assert payload['owner_members'][0]['profile_img_url'].startswith(url)

    assert len(payload['all_members']) == 1
    assert payload['all_members'][0]['u_id'] == user1['u_id'] 
    assert payload['all_members'][0]['name_first'] == 'name_1'
    assert payload['all_members'][0]['name_last'] == 'surname_1' 
    assert payload['all_members'][0]['profile_img_url'].startswith(url)
