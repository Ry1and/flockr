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
def message_edit_fixture():
    '''
    Create 4 users (3 non global owner users) and u1 creates a channel.
    Return all users and the channel id.
    '''
    other.clear()
    u_global = auth.auth_register('eG@email.com', 'passwordG', 'firstG', 'lastG')
    u1 = auth.auth_register('e1@email.com', 'password1', 'first1', 'last1')
    u2 = auth.auth_register('e2@email.com', 'password2', 'first2', 'last2')
    c_id = channels.channels_create(u1['token'], 'channel1', True)['channel_id']
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
    
def test_invalid_token_edit(message_edit_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    with pytest.raises(AccessError):
        message.message_edit('NOTATOKEN', m_id, 'Pointless')
        
def test_message_not_found(message_edit_fixture):
    '''Nonexistant message test.'''
    (_, u1, _, _) = message_edit_fixture
    with pytest.raises(InputError):
        message.message_edit(u1['token'], -42, 'Pointless')

def test_simple_edit(message_edit_fixture):
    '''U1 edits a message they sent.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    message.message_edit(u1['token'], m_id, m['message'])
    assert(margin_compare(other.search(u1['token'], 'Test Message')['messages'], []))
    assert(margin_compare(other.search(u1['token'], 'Edited Message')['messages'], [m]))
    
def test_simple_edit_remove(message_edit_fixture):
    '''U1 edits a message they sent to the empty string, deleting the message.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    message.message_edit(u1['token'], m_id, '')
    assert(margin_compare(channel.channel_messages(u1['token'], c_id, 0)['messages'], []))

def test_multiple_edit(message_edit_fixture):
    '''U1 edits two of multiple messages they sent.'''
    (_, u1, _, c_id) = message_edit_fixture
    m_id1 = message.message_send(u1['token'], c_id, 'Message 1')['message_id']
    m1 = {
        'message_id': m_id1,
        'u_id': u1['u_id'],
        'message': 'Edited 1',
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
    m_id3 = message.message_send(u1['token'], c_id, 'Message 3')['message_id']
    m3 = {
        'message_id': m_id3,
        'u_id': u1['u_id'],
        'message': 'Edited 3',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    m_id4 = message.message_send(u1['token'], c_id, 'Message 4')['message_id']
    m4 = {
        'message_id': m_id4,
        'u_id': u1['u_id'],
        'message': 'Message 4',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    message.message_edit(u1['token'], m_id1, m1['message'])
    message.message_edit(u1['token'], m_id3, m3['message'])
    assert(margin_compare(other.search(u1['token'], 'Message 1')['messages'], []))
    assert(margin_compare(other.search(u1['token'], 'Message 2')['messages'], [m2]))
    assert(margin_compare(other.search(u1['token'], 'Message 3')['messages'], []))
    assert(margin_compare(other.search(u1['token'], 'Message 4')['messages'], [m4]))
    assert(margin_compare(other.search(u1['token'], 'Edited 1')['messages'], [m1]))
    assert(margin_compare(other.search(u1['token'], 'Edited 3')['messages'], [m3]))

def test_unauthorized_user(message_edit_fixture):
    '''U2 attempts to edit a message sent by u1.'''
    (_, u1, u2, c_id) = message_edit_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    with pytest.raises(AccessError):
        message.message_edit(u2['token'], m_id, "This Shouldn't Work")

def test_owner_edit(message_edit_fixture):
    '''U1 edits a message sent by another user on the channel they are the owner
    of.'''
    (_, u1, u2, c_id) = message_edit_fixture
    channel.channel_join(u2['token'], c_id)
    m_id = message.message_send(u2['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u2['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    message.message_edit(u1['token'], m_id, m['message'])
    assert(margin_compare(other.search(u1['token'], 'Test Message')['messages'], []))
    assert(margin_compare(other.search(u1['token'], 'Edited Message')['messages'], [m]))
    
def test_global(message_edit_fixture):
    '''
    Test that a global owner can edit a message on a channel they are not an 
    owner or member of with a message they didn't send.
    '''
    (u_global, u1, _, c_id) = message_edit_fixture
    m_id = message.message_send(u1['token'], c_id, 'Test Message')['message_id']
    m = {
        'message_id': m_id,
        'u_id': u1['u_id'],
        'message': 'Edited Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    message.message_edit(u_global['token'], m_id, m['message'])
    assert(margin_compare(other.search(u1['token'], 'Test Message')['messages'], []))
    assert(margin_compare(other.search(u1['token'], 'Edited Message')['messages'], [m]))
    
