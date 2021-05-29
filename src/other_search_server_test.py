import requests
import json
from error import AccessError, InputError
import pytest
from server_test_fixtures import url
from datetime import datetime, timezone

MARGIN = 2

@pytest.fixture
def search_fixture(url):
    '''
    Create 4 users (3 non global owner users) and u1 creates a channel. Return
    all 4 users and the channel id.
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
    ''' Helper function generates timestamp of current time. '''
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
    
def test_search_invalid_token(url, search_fixture):
    '''Invalid token test case.'''
    (_, _, _, _) = search_fixture
    output = requests.get(f"{url}/search?token=NOTATOKEN&query_str=Pointless")
    assert(output.status_code == AccessError.code)

def test_search_no_messages(url, search_fixture):
    '''No messages posted test case.'''
    (_, u1, _, _) = search_fixture
    messages = requests.get(f"{url}/search?token={u1['token']}&query_str=Not Found").json()['messages']
    assert(margin_compare(messages, []))

def test_search_no_results(url, search_fixture):
    '''Query string does not match posted message.'''
    (_, u1, _, c_id) = search_fixture
    requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'})
    messages = requests.get(f"{url}/search?token={u1['token']}&query_str=Not Found").json()['messages']
    assert(margin_compare(messages, []))
    
def test_search_single_result(url, search_fixture):
    '''Query string does match posted message.'''
    (_, u1, _, c_id) = search_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = requests.get(f"{url}/search?token={u1['token']}&query_str={m['message']}").json()['messages']
    assert(margin_compare(messages, [m]))
    
def test_search_single_result_partial(url, search_fixture):
    '''Query string is a substring of a posted message.'''
    (_, u1, _, c_id) = search_fixture
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = requests.get(f"{url}/search?token={u1['token']}&query_str=st M").json()['messages']
    assert(margin_compare(messages, [m]))
    
def test_search_multiple_results(url, search_fixture):
    '''Query string matches 2 of 3 posted messaged.'''
    (_, u1, _, c_id) = search_fixture
    m_id1 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Message 1'}).json()['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Message 1',
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
        'channel_id': c_id, 'message': 'Other 3'}).json()['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Other 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Other").json()['messages']
    assert(margin_compare(messages1, [m1, m2]))
    assert(margin_compare(messages2, [m3]))

def test_search_multiple_channels(url, search_fixture):
    '''Same as previous test case but accross 3 channels.'''
    (_, u1, _, c_id1) = search_fixture
    c_id2 = (requests.post(f'{url}/channels/create', json = {'token': u1['token'],
        'name': 'channel2', 'is_public': True}).json())['channel_id']
    c_id3 = (requests.post(f'{url}/channels/create', json = {'token': u1['token'],
        'name': 'channel3', 'is_public': True}).json())['channel_id']
    m_id1 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id1, 'message': 'Message 1'}).json()['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Message 1',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id2 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id2, 'message': 'Message 2'}).json()['message_id']
    m2 = {
        'message_id': m_id2,
        'u_id': u1['u_id'],
        'message': 'Message 2',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id3 = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id3, 'message': 'Other 3'}).json()['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Other 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages1 = requests.get(f"{url}/search?token={u1['token']}&query_str=Message").json()['messages']
    messages2 = requests.get(f"{url}/search?token={u1['token']}&query_str=Other").json()['messages']
    assert(margin_compare(messages1, [m1, m2]))
    assert(margin_compare(messages2, [m3]))
    
def test_global_owner(url, search_fixture):
    '''Test a global owner can call search.'''
    (u_global, u1, _, c_id) = search_fixture
    requests.post(f'{url}/channel/join', json = {'token': u_global['token'],
        'channel_id': c_id})
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = requests.get(f"{url}/search?token={u_global['token']}&query_str=Test Message").json()['messages']
    assert(margin_compare(messages, [m]))
    
def test_not_channel_member(url, search_fixture):
    '''
    Search is called with a query string that matches a message, but
    the user calling search is not a member of the channel the message was
    posted to.
    '''
    (_, u1, u2, c_id) = search_fixture
    requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    messages = requests.get(f"{url}/search?token={u2['token']}&query_str=Test Message").json()['messages']
    assert(margin_compare(messages, []))
    
def test_channel_member(url, search_fixture):
    ''' Search called by a non-owner member of a channel.'''
    (_, u1, u2, c_id) = search_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    m_id = requests.post(f'{url}/message/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'}).json()['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = requests.get(f"{url}/search?token={u2['token']}&query_str=Test Message").json()['messages']
    assert(margin_compare(messages, [m]))
