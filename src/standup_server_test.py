import server
import pytest
import requests
from datetime import timezone, datetime
from error import AccessError, InputError
from server_test_fixtures import url
from time import sleep

MARGIN = 2

@pytest.fixture
def standup_fixture(url):
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
    
#-----------------------------standup/start-------------------------------------
def test_start_invalid_token(url, standup_fixture):
    '''Invalid token test.'''
    (_, _, _, c_id) = standup_fixture
    output = requests.post(f'{url}/standup/start', json = {'token': 'NotAToken',
        'channel_id': c_id, 'length': 60})
    assert(output.status_code == AccessError.code)
    
def test_start_invalid_c_id(url, standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, _) = standup_fixture
    output = requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': -42, 'length': 60})
    assert(output.status_code == InputError.code)
    
def test_start_already_standup(url, standup_fixture):
    '''Standup already running case.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    assert(output.status_code == InputError.code)
    
def test_start_successful_standup(url, standup_fixture):
    '''Test if a standup can be successfully started.'''
    (_, u1, _, c_id) = standup_fixture
    time_finish = requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60}).json()['time_finish']
    standup = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id={c_id}").json()
    s_time = get_current_timestamp()
    assert(standup['is_active'] == True)
    assert(standup['time_finish'] == time_finish)
    assert(abs(standup['time_finish'] - (s_time + 60)) <= MARGIN)
    
def test_end_successful_standup(url, standup_fixture):
    '''Test that a standup ends after it's duration is up.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 1})
    sleep(2)
    standup = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id={c_id}").json()
    assert(standup['is_active'] == False)
    assert(standup['time_finish'] == None)
    
def test_start_successful_standup_member(url, standup_fixture):
    '''Test if a standup can be successfully started by a channel member.'''
    (_, _, u2, c_id) = standup_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    time_finish = requests.post(f'{url}/standup/start', json = {'token': u2['token'],
        'channel_id': c_id, 'length': 60}).json()['time_finish']
    standup = requests.get(f"{url}/standup/active?token={u2['token']}&channel_id={c_id}").json()
    s_time = get_current_timestamp()
    assert(standup['is_active'] == True)
    assert(standup['time_finish'] == time_finish)
    assert(abs(standup['time_finish'] - (s_time + 60)) <= MARGIN)
    
def test_end_successful_standup_member(url, standup_fixture):
    '''
    Test that a standup ends after it's duration is up when started by a
    channel member.
    '''
    (_, _, u2, c_id) = standup_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    requests.post(f'{url}/standup/start', json = {'token': u2['token'],
        'channel_id': c_id, 'length': 1})
    sleep(2)
    standup = requests.get(f"{url}/standup/active?token={u2['token']}&channel_id={c_id}").json()
    assert(standup['is_active'] == False)
    assert(standup['time_finish'] == None)

def test_negative_duration(url, standup_fixture):
    '''Test that standup started with negative duration ends immediately.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': -50})
    standup = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id={c_id}").json()
    assert(standup['is_active'] == False)
    assert(standup['time_finish'] == None)
    
#-----------------------------standup/active------------------------------------
def test_active_invalid_token(url, standup_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.get(f"{url}/standup/active?token=NotAToken&channel_id={c_id}")
    assert(output.status_code == AccessError.code)
    
def test_active_invalid_c_id(url, standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id=-42")
    assert(output.status_code == InputError.code)
    
def test_active_no_standup(url, standup_fixture):
    '''No standup running test.'''
    (_, u1, _, c_id) = standup_fixture
    standup = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id={c_id}").json()
    assert(standup['is_active'] == False)
    assert(standup['time_finish'] == None)

def test_active_standup(url, standup_fixture):
    '''Standup running test.'''
    (_, u1, _, c_id) = standup_fixture
    time_finish = requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60}).json()['time_finish']
    standup = requests.get(f"{url}/standup/active?token={u1['token']}&channel_id={c_id}").json()
    s_time = get_current_timestamp()
    assert(standup['is_active'] == True)
    assert(standup['time_finish'] == time_finish)
    assert(abs(standup['time_finish'] - (s_time + 60)) <= MARGIN)

def test_active_standup_other_user(url, standup_fixture):
    '''Standup running and called by a user who didn't start the standup.'''
    (_, u1, u2, c_id) = standup_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    time_finish = requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60}).json()['time_finish']
    standup = requests.get(f"{url}/standup/active?token={u2['token']}&channel_id={c_id}").json()
    s_time = get_current_timestamp()
    assert(standup['is_active'] == True)
    assert(standup['time_finish'] == time_finish)
    assert(abs(standup['time_finish'] - (s_time + 60)) <= MARGIN)

#-----------------------------standup/send--------------------------------------
def test_send_invalid_token(url, standup_fixture):
    '''Invalid token test.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.post(f'{url}/standup/send', json = {'token': 'NotAToken',
        'channel_id': c_id, 'message': 'Test Message'})
    assert(output.status_code == AccessError.code)
    
def test_send_invalid_c_id(url, standup_fixture):
    '''Invalid c_id test.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': -42, 'message': 'Test Message'})
    assert(output.status_code == InputError.code)
    
def test_send_invalid_message(url, standup_fixture):
    '''Invalid message test.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'A' * 1500})
    assert(output.status_code == InputError.code)
    
def test_send_no_standup(url, standup_fixture):
    '''No standup running to send to case.'''
    (_, u1, _, c_id) = standup_fixture
    output = requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'})
    assert(output.status_code == InputError.code)
    
def test_send_not_member(url, standup_fixture):
    '''Sender not a member of the channel case.'''
    (_, u1, u2, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 60})
    output = requests.post(f'{url}/standup/send', json = {'token': u2['token'],
        'channel_id': c_id, 'message': 'Test Message'})
    assert(output.status_code == AccessError.code)

def test_send_single_messsage(url, standup_fixture):
    '''User sends a message before the standup ends.'''
    (_, u1, _, c_id) = standup_fixture
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 1})
    requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message'})
    sleep(2)
    m = {
        'message_id': 0,
        'u_id': u1['u_id'],
        'message': 'first1last1: Test Message',
        'time_created': get_current_timestamp(),
        'reacts': [],
        'is_pinned': False,
    }
    messages = requests.get(f"{url}/channel/messages?token={u1['token']}&channel_id={c_id}&start=0").json()['messages']
    assert(messages[0]['time_created'] - m['time_created'] <= MARGIN)
    m['time_created'] = messages[0]['time_created']
    assert(margin_compare(messages, [m]))
    
def test_send_multi_messsage(url, standup_fixture):
    '''Users send multiple messages before the standup ends.'''
    (_, u1, u2, c_id) = standup_fixture
    requests.post(f'{url}/channel/join', json = {'token': u2['token'],
        'channel_id': c_id})
    requests.post(f'{url}/standup/start', json = {'token': u1['token'],
        'channel_id': c_id, 'length': 1})
    requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message 1'})
    requests.post(f'{url}/standup/send', json = {'token': u2['token'],
        'channel_id': c_id, 'message': 'Test Message 2'})
    requests.post(f'{url}/standup/send', json = {'token': u1['token'],
        'channel_id': c_id, 'message': 'Test Message 3'})
    requests.post(f'{url}/standup/send', json = {'token': u2['token'],
        'channel_id': c_id, 'message': 'Test Message 4'})
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
    messages = requests.get(f"{url}/channel/messages?token={u1['token']}&channel_id={c_id}&start=0").json()['messages']
    assert(margin_compare(messages, [m]))
