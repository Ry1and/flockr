import pytest
import standup
import auth
import channel
import channels
import other
from datetime import timezone, datetime
from error import AccessError, InputError
from time import sleep

MARGIN = 2

@pytest.fixture
def standup_fixture():
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
    
#-----------------------------standup/start-------------------------------------
def test_start_invalid_token(standup_fixture):
    '''Invalid token test.'''
    (_, _, _, c_id) = standup_fixture
    with pytest.raises(AccessError):
        standup.standup_start('NotAToken', c_id, 60)
    
def test_start_invalid_c_id(standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, _) = standup_fixture
    with pytest.raises(InputError):
        standup.standup_start(u1['token'], -42, 60)
    
def test_start_already_standup(standup_fixture):
    '''Standup already running case.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(InputError):
        standup.standup_start(u1['token'], c_id, 60)
    
def test_start_successful_standup(standup_fixture):
    '''Test if a standup can be successfully started.'''
    (_, u1, _, c_id) = standup_fixture
    time_finish = standup.standup_start(u1['token'], c_id, 60)['time_finish']
    s = standup.standup_active(u1['token'], c_id)
    s_time = get_current_timestamp()
    assert(s['is_active'] == True)
    assert(s['time_finish'] == time_finish)
    assert(abs(s['time_finish'] - (s_time + 60)) <= MARGIN)
    
def test_end_successful_standup(standup_fixture):
    '''Test that a standup ends after it's duration is up.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 1)
    sleep(2)
    s = standup.standup_active(u1['token'], c_id)
    assert(s['is_active'] == False)
    assert(s['time_finish'] == None)
    
def test_start_successful_standup_member(standup_fixture):
    '''Test if a standup can be successfully started by a channel member.'''
    (_, _, u2, c_id) = standup_fixture
    channel.channel_join(u2['token'], c_id)
    time_finish = standup.standup_start(u2['token'], c_id, 60)['time_finish']
    s = standup.standup_active(u2['token'], c_id)
    s_time = get_current_timestamp()
    assert(s['is_active'] == True)
    assert(s['time_finish'] == time_finish)
    assert(abs(s['time_finish'] - (s_time + 60)) <= MARGIN)
    
def test_end_successful_standup_member(standup_fixture):
    '''
    Test that a standup ends after it's duration is up when started by a
    channel member.
    '''
    (_, _, u2, c_id) = standup_fixture
    channel.channel_join(u2['token'], c_id)
    standup.standup_start(u2['token'], c_id, 1)
    sleep(2)
    s = standup.standup_active(u2['token'], c_id)
    assert(s['is_active'] == False)
    assert(s['time_finish'] == None)

def test_negative_duration(standup_fixture):
    '''Test that standup started with negative duration ends immediately.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, -50)
    s = standup.standup_active(u1['token'], c_id)
    assert(s['is_active'] == False)
    assert(s['time_finish'] == None)
    
#-----------------------------standup/active------------------------------------
def test_active_invalid_token(standup_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(AccessError):
        standup.standup_active('NotAToken', c_id)
    
def test_active_invalid_c_id(standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(InputError):
        standup.standup_active(u1['token'], -42)
    
def test_active_no_standup(standup_fixture):
    '''No standup running test.'''
    (_, u1, _, c_id) = standup_fixture
    s = standup.standup_active(u1['token'], c_id)
    assert(s['is_active'] == False)
    assert(s['time_finish'] == None)

def test_active_standup(standup_fixture):
    '''Standup running test.'''
    (_, u1, _, c_id) = standup_fixture
    time_finish = standup.standup_start(u1['token'], c_id, 60)['time_finish']
    s = standup.standup_active(u1['token'], c_id)
    s_time = get_current_timestamp()
    assert(s['is_active'] == True)
    assert(s['time_finish'] == time_finish)
    assert(abs(s['time_finish'] - (s_time + 60)) <= MARGIN)

def test_active_standup_other_user(standup_fixture):
    '''Standup running and called by a user who didn't start the standup.'''
    (_, u1, u2, c_id) = standup_fixture
    channel.channel_join(u2['token'], c_id)
    time_finish = standup.standup_start(u1['token'], c_id, 60)['time_finish']
    s = standup.standup_active(u2['token'], c_id)
    s_time = get_current_timestamp()
    assert(s['is_active'] == True)
    assert(s['time_finish'] == time_finish)
    assert(abs(s['time_finish'] - (s_time + 60)) <= MARGIN)
    
#-----------------------------standup/send--------------------------------------
def test_send_invalid_token(standup_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(AccessError):
        standup.standup_send('NotAToken', c_id, 'Test Message')
    
def test_send_invalid_c_id(standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(InputError):
        standup.standup_send(u1['token'], -42, 'Test Message')
    
def test_send_invalid_message(standup_fixture):
    '''Invalid message test.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(InputError):
        standup.standup_send(u1['token'], c_id, 'A' * 1500)
    
def test_send_no_standup(standup_fixture):
    '''No standup running to send to case.'''
    (_, u1, _, c_id) = standup_fixture
    with pytest.raises(InputError):
        standup.standup_send(u1['token'], c_id, 'Test Message')
    
def test_send_not_member(standup_fixture):
    '''Sender not a member of the channel case.'''
    (_, u1, u2, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 60)
    with pytest.raises(AccessError):
        standup.standup_send(u2['token'], c_id, 'Test Message')

def test_send_single_messsage(standup_fixture):
    '''User sends a message before the standup ends.'''
    (_, u1, _, c_id) = standup_fixture
    standup.standup_start(u1['token'], c_id, 1)
    standup.standup_send(u1['token'], c_id, 'Test Message')
    sleep(2)
    m = {
        'message_id': 0,
        'u_id': u1['u_id'],
        'message': 'first1last1: Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = channel.channel_messages(u1['token'], c_id, 0)['messages']
    assert(margin_compare(messages, [m]))
    
def test_send_multi_messsage(standup_fixture):
    '''Users send multiple messages before the standup ends.'''
    (_, u1, u2, c_id) = standup_fixture
    channel.channel_join(u2['token'], c_id)
    standup.standup_start(u1['token'], c_id, 1)
    standup.standup_send(u1['token'], c_id, 'Test Message 1')
    standup.standup_send(u2['token'], c_id, 'Test Message 2')
    standup.standup_send(u1['token'], c_id, 'Test Message 3')
    standup.standup_send(u2['token'], c_id, 'Test Message 4')
    sleep(2)
    m = {
        'message_id': 0,
        'u_id': u1['u_id'],
        'message': '''first1last1: Test Message 1
first2last2: Test Message 2
first1last1: Test Message 3
first2last2: Test Message 4''',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = channel.channel_messages(u1['token'], c_id, 0)['messages']
    assert(margin_compare(messages, [m]))
