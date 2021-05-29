import requests
import json
from error import AccessError, InputError
import pytest
from server_test_fixtures import url
from datetime import timezone, datetime

MARGIN = 2

@pytest.fixture(autouse=True)
def clear_only(url):
    requests.delete(f'{url}/clear')

@pytest.fixture
def message_edit_fixture(url):
    '''
    Create 4 users (3 non global owner users) and u1 creates a channel.
    Return all users and the channel id.
    '''
    requests.delete(f'{url}/clear')
    u_global = requests.post(f'{url}/auth/register', json = {'email': 'eG@email.com',
        'password': 'passwordG', 'name_first': 'firstG', 'name_last': 'lastG'}).json()
    u1 = requests.post(f'{url}/auth/register', json = {'email': 'e1@email.com',
        'password': 'password1', 'name_first': 'first1', 'name_last': 'last1'}).json()
    u2 = requests.post(f'{url}/auth/register', json = {'email': 'e2@email.com',
        'password': 'password2', 'name_first': 'first2', 'name_last': 'last2'}).json()
    c_id = (requests.post(f'{url}/channels/create', json = {'token': u1['token'],
        'name': 'channel1', 'is_public': True}).json())['channel_id']
    return (u_global, u1, u2, c_id)

def get_current_timestamp():
    '''Helper function generates timestamp of current time.'''
    dt = datetime.utcnow()
    timestamp = int(dt.replace(tzinfo = timezone.utc).timestamp())
    return timestamp
    
def margin_compare(l1, l2):
    '''
    Compares two lists of messages allowing for a margin of error in the
    time_created parameters.
    '''
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if abs(l1[i]['time_created'] - l2[i]['time_created']) > MARGIN:
            return False
        l1[i]['time_created'] = l2[i]['time_created']
        if l1[i] != l2[i]:
            return False
    return True
    
def test_invalid_token_edit(url, message_edit_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    output = requests.put(f'{url}/message/edit', json = {'token': 'NotAToken',
        'message_id': m_id, 'message': 'Pointless'})
    assert(output.status_code == AccessError.code)

def test_message_not_found(url, message_edit_fixture):
    '''Nonexistant message test.'''
    (_, u1, _, _) = message_edit_fixture
    output = requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': -50, 'message': 'Pointless'})
    assert(output.status_code == InputError.code)

def test_simple_edit(url, message_edit_fixture):
    '''U1 edits a message they sent.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': m_id, 'message':m['message']})
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Test Message").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Edited Message").json()['messages']
    assert(margin_compare(messages1, []))
    assert(margin_compare(messages2, [m]))
    
def test_simple_edit_remove(url, message_edit_fixture):
    '''U1 edits a message they sent to the empty string, deleting the message.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': m_id, 'message':''})
    messages = requests.get(f"{url}/channel/messages?token={u1['token']}&channel_id={c_id}&start=0").json()['messages']
    assert(margin_compare(messages, []))

def test_multiple_edit(url, message_edit_fixture):
    '''U1 edits two of multiple messages they sent.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id1 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Message 1'}).json()['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Edited 1',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id2 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Message 2'}).json()['message_id']
    m2 = {
        'message_id': m_id2,
        'u_id': u1['u_id'],
        'message': 'Message 2',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id3 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Message 3'}).json()['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Edited 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id4 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Message 4'}).json()['message_id']
    m4 = {
        'message_id': m_id4,
        'u_id': u1['u_id'],
        'message': 'Message 4',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': m_id1, 'message':m1['message']})
    requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': m_id3, 'message':m3['message']})
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message 1").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message 2").json()['messages']
    messages3 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message 3").json()['messages']
    messages4 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message 4").json()['messages']
    edited1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Edited 1").json()['messages']
    edited3 = requests.get(f"{url}/search?token={u1['token']}&query_str=Edited 3").json()['messages']
    assert(margin_compare(messages1, []))
    assert(margin_compare(messages2, [m2]))
    assert(margin_compare(messages3, []))
    assert(margin_compare(messages4, [m4]))
    assert(margin_compare(edited1, [m1]))
    assert(margin_compare(edited3, [m3]))

def test_unauthorized_user(url, message_edit_fixture):
    '''U2 attempts to edit a message sent by u1.'''
    (_, u1, u2, c_id) = message_edit_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    output = requests.put(f'{url}/message/edit', json = {'token': u2['token'],
        'message_id': m_id, 'message': "This Shouldn't Work"})
    assert(output.status_code == AccessError.code)
    
def test_owner_edit(url, message_edit_fixture):
    '''U1 edits a message sent by another user on the channel they are the owner
    of.'''
    (_, u1, u2, c_id) = message_edit_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    m_id = requests.post(f'{url}/message/send', json = {'token': u2['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u2['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    requests.put(f'{url}/message/edit', json = {'token': u1['token'],
        'message_id': m_id, 'message': m['message']})
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Test Message").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Edited Message").json()['messages']
    assert(margin_compare(messages1, []))
    assert(margin_compare(messages2, [m]))

def test_global(url, message_edit_fixture):
    '''
    Test that a global owner can edit a message on a channel they are not an 
    owner or member of with a message they didn't send.
    '''
    (u_global, u1, _, c_id) = message_edit_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    requests.put(f'{url}/message/edit', json = {'token': u_global['token'],
        'message_id': m_id, 'message': m['message']})
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Test Message").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Edited Message").json()['messages']
    assert(margin_compare(messages1, []))
    assert(margin_compare(messages2, [m]))

