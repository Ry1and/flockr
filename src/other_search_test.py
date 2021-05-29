import auth
import channel
import channels
import message
import other
import pytest
from datetime import timezone, datetime
from error import AccessError, InputError

MARGIN = 2

@pytest.fixture
def search_fixture():
    '''
    Create 4 users (3 non global owner users) and u1 creates a channel. Return
    all 4 users and the channel id.
    '''
    other.clear()
    u_global = auth.auth_register('eG@email.com', 'passwordG', 'firstG', 'lastG')
    u1 = auth.auth_register('e1@email.com', 'password1', 'first1', 'last1')
    u2 = auth.auth_register('e2@email.com', 'password2', 'first2', 'last2')
    c_id = channels.channels_create(u1['token'], 'channel1', True)['channel_id']
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

def test_search_invalid_token(search_fixture):
    '''Invalid token test case.'''
    (_, _, _, _) = search_fixture
    with pytest.raises(AccessError):
        other.search('NOTATOKEN', 'Pointless')

def test_search_no_messages(search_fixture):
    '''No messages posted test case.'''
    (_, u1, _, _) = search_fixture
    assert(margin_compare(other.search(u1['token'], 'Pointless')['messages'], []))

def test_search_no_results(search_fixture):
    '''Query string does not match posted message.'''
    (_, u1, _, c_id) = search_fixture
    message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    assert(margin_compare(other.search(u1['token'], 'Not Message')['messages'], []))

def test_search_single_result(search_fixture):
    '''Query string does match posted message.'''
    (_, u1, _, c_id) = search_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u1['token'], m['message'])['messages'], [m]))
    
def test_search_single_result_partial(search_fixture):
    '''Query string is a substring of a posted message.'''
    (_, u1, _, c_id) = search_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u1['token'], 'st M')['messages'], [m]))
    
def test_search_multiple_results(search_fixture):
    '''Query string matches 2 of 3 posted messaged.'''
    (_, u1, _, c_id) = search_fixture
    m_id1 = message.message_send(u1['token'], c_id, 'Message 1')['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Message 1',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id2 = message.message_send(u1['token'], c_id, 'Message 2')['message_id']
    m2 = {
        'message_id': m_id2,
        'u_id': u1['u_id'],
        'message': 'Message 2',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id3 = message.message_send(u1['token'], c_id, 'Other 3')['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Other 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u1['token'], 'Message')['messages'], [m1, m2]))
    assert(margin_compare(other.search(u1['token'], 'Other')['messages'], [m3]))

def test_search_multiple_channels(search_fixture):
    '''Same as previous test case but accross 3 channels.'''
    (_, u1, _, c_id1) = search_fixture
    c_id2 = channels.channels_create(u1['token'], 'channel2', True)['channel_id']
    c_id3 = channels.channels_create(u1['token'], 'channel3', True)['channel_id']
    m_id1 = message.message_send(u1['token'], c_id1, 'Message 1')['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Message 1',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id2 = message.message_send(u1['token'], c_id2, 'Message 2')['message_id']
    m2 = {
        'message_id': m_id2,
        'u_id': u1['u_id'],
        'message': 'Message 2',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id3 = message.message_send(u1['token'], c_id3, 'Other 3')['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Other 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u1['token'], 'Message')['messages'], [m1, m2]))
    assert(margin_compare(other.search(u1['token'], 'Other')['messages'], [m3]))
    
def test_global_owner(search_fixture):
    '''Test a global owner can call search.'''
    (u_global, u1, _, c_id) = search_fixture
    channel.channel_join(u_global['token'], c_id)
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u1['token'], 'Test Message')['messages'], [m]))
    
def test_not_channel_member(search_fixture):
    '''
    Search is called with a query string that matches a message, but
    the user calling search is not a member of the channel the message was
    posted to.
    '''
    (_, u1, u2, c_id) = search_fixture
    message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    assert(margin_compare(other.search(u2['token'], 'Test Message')['messages'], []))
    
def test_channel_member(search_fixture):
    ''' Search called by a non-owner member of a channel.'''
    (_, u1, u2, c_id) = search_fixture
    channel.channel_join(u2['token'], c_id)
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    assert(margin_compare(other.search(u2['token'], 'Test Message')['messages'], [m]))
    
