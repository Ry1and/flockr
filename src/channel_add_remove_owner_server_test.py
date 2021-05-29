import requests
import json
from error import AccessError, InputError
import pytest
from server_test_fixtures import url

@pytest.fixture
def add_remove_fixture(url):
    '''
    A fixture that creates 4 users (3 non global owner users) and
    u1 also creates a channel. 4 users and c_id are returned.
    '''
    requests.delete(f'{url}/clear')
    u_global = requests.post(f'{url}/auth/register', json = {'email': 'eG@email.com',
        'password': 'passwordG', 'name_first': 'firstG', 'name_last': 'lastG'}).json()
    u1 = requests.post(f'{url}/auth/register', json = {'email': 'e1@email.com',
        'password': 'password1', 'name_first': 'first1', 'name_last': 'last1'}).json()
    u2 = requests.post(f'{url}/auth/register', json = {'email': 'e2@email.com',
        'password': 'password2', 'name_first': 'first2', 'name_last': 'last2'}).json()
    u3 = requests.post(f'{url}/auth/register', json = {'email': 'e3@email.com',
        'password': 'password3', 'name_first': 'first3', 'name_last': 'last3'}).json()
    c_id = (requests.post(f'{url}/channels/create', json = {'token': u1['token'],
        'name': 'channel1', 'is_public': True}).json())['channel_id']
    return (u_global, u1, u2, u3, c_id)

def test_channel_addowner_global_owner(url, add_remove_fixture):
    '''
    Tests that a global owner can add anyone to any channel as an owner.
    '''
    (u_global, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u_global['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    assert(any(u2['u_id'] == owner['u_id'] for owner in details['owner_members']))

def test_channel_addowner_two_users(url, add_remove_fixture):
    '''
    Tests that the owner of a channel (u1) can add another user (u2) as an 
    owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    assert(any(u2['u_id'] == owner['u_id'] for owner in details['owner_members']))
    
def test_channel_addowner_three_users(url, add_remove_fixture):
    '''
    Tests that owner permissions correctly apply to u2 after the prior test
    case by testing that u2 can now add u3 as an owner of the channel.
    '''
    (_, u1, u2, u3, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    requests.post(f'{url}/channel/addowner', json = {'token': u2['token'],
        'channel_id': c_id, 'u_id': u3['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    assert(any(u2['u_id'] == owner['u_id'] for owner in details['owner_members']))
    assert(any(u3['u_id'] == owner['u_id'] for owner in details['owner_members']))
    
def test_channel_addowner_invalid_channel_id(url, add_remove_fixture):
    '''
    Tests that an InputError is raised when an invalid channel_id is provided.
    '''
    (_, u1, u2, _, _) = add_remove_fixture
    status = requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': -42, 'u_id': u2['u_id']})
    assert(status.status_code == InputError.code)
    
def test_channel_addowner_add_self(url, add_remove_fixture):
    '''
    Tests that an InputError is raised if an owner attempts to add themselves
    as an owner of the channel they are already an owner of.
    '''
    (_, u1, _, _, c_id) = add_remove_fixture
    status = requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u1['u_id']})
    assert(status.status_code == InputError.code)

def test_channel_addowner_add_within(url, add_remove_fixture):
    '''
    Tests that an InputError is raised if another owner tries to add a user who 
    is already an owner of a channel as an owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    status = requests.post(f'{url}/channel/addowner', json = {'token': u2['token'],
        'channel_id': c_id, 'u_id': u1['u_id']})
    assert(status.status_code == InputError.code)

def test_channel_addowner_add_unauthorized(url, add_remove_fixture):
    '''
    Tests that an AccessError is raised if a member but not an owner of a
    channel tries to add another non-owner user as an owner.
    '''
    (_, _, u2, u3, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    status = requests.post(f'{url}/channel/addowner', json = {'token': u2['token'],
        'channel_id': c_id, 'u_id': u3['u_id']})
    assert(status.status_code == AccessError.code)

def test_channel_addowner_already_joined(url, add_remove_fixture):
    '''
    Tests that a member can be correctly added as an owner of a channel by
    an authorized user.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    assert(any(u2['u_id'] == owner['u_id'] for owner in details['owner_members']))

def test_channel_addowner_invalid_token(url, add_remove_fixture):
    '''
    Tests that an AccessError is raised if an invalid token is given.
    '''
    (_, _, u2, _, c_id) = (add_remove_fixture)
    status = requests.post(f'{url}/channel/addowner', json = {'token': 'NotAToken',
        'channel_id': c_id, 'u_id': u2['u_id']})
    assert(status.status_code == AccessError.code)
    
def test_channel_removeowner_global_owner(url, add_remove_fixture):
    '''
    Tests that a global owner can remove anyone as an owner from any channel.
    '''
    (u_global, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    requests.post(f'{url}/channel/removeowner', json = {'token': u_global['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    c_owners = details['owner_members']
    c_members = details['all_members']
    assert(not any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u2['u_id'] == member['u_id'] for member in c_members))
    
def test_channel_removeowner_new_owner(url, add_remove_fixture):
    '''
    Tests that an owner can correctly remove a user as an owner of a channel
    after adding them as an owner.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    requests.post(f'{url}/channel/removeowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    c_owners = details['owner_members']
    c_members = details['all_members']
    assert(not any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u2['u_id'] == member['u_id'] for member in c_members))

def test_channel_removeowner_original_creator(url, add_remove_fixture):
    '''
    Tests that a newly added owner of a channel can remove the user who made
    them an owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    requests.post(f'{url}/channel/removeowner', json = {'token': u2['token'],
        'channel_id': c_id, 'u_id': u1['u_id']})
    details = requests.get(f"{url}/channel/details?token={u1['token']}&channel_id={c_id}").json()
    c_owners = details['owner_members']
    c_members = details['all_members']
    assert(not any(u1['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u1['u_id'] == member['u_id'] for member in c_members))
    
def test_channel_remove_owner_bad_channel_id(url, add_remove_fixture):
    '''
    Tests that an InputError is raised if an invalid channel_id is provided.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    status = requests.post(f'{url}/channel/removeowner', json = {'token': u1['token'],
        'channel_id': -42, 'u_id': u2['u_id']})
    assert(status.status_code == InputError.code)

def test_channel_removeowner_non_member(url, add_remove_fixture):
    '''
    Tests that an InputError is raised if the user being removed as an owner
    isn't a member or owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    status = requests.post(f'{url}/channel/removeowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    assert(status.status_code == InputError.code)

def test_channel_removeowner_self_removal(url, add_remove_fixture):
    '''
    Tests that an InputError is raised when an owner attempts to remove
    themselves as an owner.
    '''
    (_, u1, _, _, c_id) = add_remove_fixture
    status = requests.post(f'{url}/channel/removeowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u1['u_id']})
    assert(status.status_code == InputError.code)

def test_channel_removeowner_non_owner(url, add_remove_fixture):
    '''
    Tests that an InputError is raised if the user being removed as an owner
    isn't an owner of the channel but is a member of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    status = requests.post(f'{url}/channel/removeowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    assert(status.status_code == InputError.code)
    
def test_channel_removeowner_unauthorized(url, add_remove_fixture):
    '''
    Tests that an AccessError is raised if the user calling the function isn't 
    an owner of the channel but is a member of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    status = requests.post(f'{url}/channel/removeowner', json = {'token': u2['token'],
        'channel_id': c_id, 'u_id': u1['u_id']})
    assert(status.status_code == AccessError.code)
    
def test_channel_removeowner_invalid_token(url, add_remove_fixture):
    '''
    Tests that an AccessError is raised if an invalid token is provided.
    '''
    (_, u1, u2, _, c_id) = (add_remove_fixture)
    requests.post(f'{url}/channel/addowner', json = {'token': u1['token'],
        'channel_id': c_id, 'u_id': u2['u_id']})
    status = requests.post(f'{url}/channel/removeowner', json = {'token': 'NotAToken',
        'channel_id': c_id, 'u_id': u2['u_id']})
    assert(status.status_code == AccessError.code)
