import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels
from datetime import datetime as dt, timezone, timedelta


@pytest.fixture
def initialise_send_later(url, register_users):
    (user0, user1, _) = register_users

    #user0 creates a public channel
    c_name = "public_channel"
    c_id = (requests.post(f"{url}/channels/create",
                          json={
                              'token': user0['token'],
                              'name': c_name,
                              'is_public': True
                          }).json())['channel_id']

    m = "test"
    time_sent = dt.utcnow() + timedelta(minutes=1)
    time_sent = int(time_sent.replace(tzinfo=timezone.utc).timestamp())
    return (url, user0, user1, c_id, m, time_sent)


def test_sanity(url):
    '''Test to check if the server is running '''
    assert url.startswith("http")


def test_invalid_token(initialise_send_later):
    '''Test with an invalid token'''
    (url, _, _, c_id, m, time_sent) = initialise_send_later
    

    m_id = requests.post(f"{url}/message/sendlater",
                         json={
                             'token': 'invalid',
                             'channel_id': c_id,
                             'message' : m,
                             'time_sent' : time_sent
                         })
    
    # assert 1 == 2
    assert m_id.status_code == AccessError.code

def test_invalid_channel_id(initialise_send_later):
    '''Test with an invalid channel'''
    (url, user0, _, _, m, time_sent) = initialise_send_later

    m_id = requests.post(f"{url}/message/sendlater",
                         json={
                             'token': user0['token'],
                             'channel_id': -42,
                             'message' : m,
                             'time_sent' : time_sent
                         })
    
    assert m_id.status_code == InputError.code

def test_message_too_long(initialise_send_later):
    ''' test with a message thats too long'''
    (url, user0, _, c_id, m, time_sent) = initialise_send_later

    m = m * 300
    m_id = requests.post(f"{url}/message/sendlater",
                         json={
                             'token': user0['token'],
                             'channel_id': c_id,
                             'message' : m,
                             'time_sent' : time_sent,
                         })
    
    assert m_id.status_code == InputError.code


def test_invalid_time(initialise_send_later):
    ''' test trying to send a message into the past'''
    (url, user0, _, c_id, m, time_sent) = initialise_send_later

    time_sent = dt.utcnow() - timedelta(minutes=7)
    time_sent = int(time_sent.replace(tzinfo=timezone.utc).timestamp())
    
    m_id = requests.post(f"{url}/message/sendlater",
                         json={
                             'token': user0['token'],
                             'channel_id': c_id,
                             'message' : m,
                             'time_sent' : time_sent,
                         })

    assert m_id.status_code == InputError.code


def test_not_member(initialise_send_later):
    '''Test when the user is not a member of the channel'''
    (url, _, user1, c_id, m, time_sent) = initialise_send_later

    m_id = requests.post(f"{url}/message/sendlater",
                         json={
                             'token': user1['token'],
                             'channel_id': c_id,
                             'message' : m,
                             'time_sent' : time_sent,
                         })
    
    assert m_id.status_code == AccessError.code


def test_send_1_minute(initialise_send_later):
    '''
    Ensure that no messages are sent as soon as the send_later 
    function is executed
    '''
    (url, user0, _, c_id, m, time_sent) = initialise_send_later

    requests.post(f"{url}/message/sendlater",
                         json={
                             'token': user0['token'],
                             'channel_id': c_id,
                             'message' : m,
                             'time_sent' : time_sent,
                         })
    
    messages = requests.get(
        f"{url}/channel/messages?token={user0['token']}&channel_id={c_id}&start={0}"
    )

    assert messages.json()['messages'] == []




    


    



    

    
    





