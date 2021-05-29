import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels

'''File for testing the http wrapping for '''



def test_sanity(url):
    ''' Test to check if the server has started'''
    assert url.startswith("http")


def test_invalid_token(url,register_users):
    '''Test to check if the correct error is raised when an invalid token is provided'''
    
    (user1,_,_) = register_users

    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': True
        }).json())['channel_id']
    
    start = 0
    token = 'invalidtoken'
    messages = requests.get(f"{url}/channel/messages?token={token}&channel_id={c_id}&start={start}")
    assert messages.status_code == AccessError.code


def test_invalid_channel(url,register_users):
    '''When the channel_id is invalid, raise an Input error'''
    (user1,_,_) = register_users

    start = 0
    c_id = -42
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    assert messages.status_code == InputError.code

def test_not_member(url, register_users):
    ''' When the user is not a member of the channel, raise an Accesserror'''

    (user1,user2,_) = register_users

    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': True
        }).json())['channel_id']

    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user2['token']}&channel_id={c_id}&start={start}")

    assert messages.status_code == AccessError.code



def test_invalid_start(url, register_users):
    '''When the user enters an inalid number for the start index for the returned messages list'''
    (user1,_,_) = register_users
    
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': True
        }).json())['channel_id']

    start = 100

    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    assert messages.status_code == InputError.code
    


def test_single_message_pub(url, register_users):
    '''Retrieving messages of a public channel as an authorised user'''
    
    (user1,_,_) = register_users
    
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': True
        }).json())['channel_id']

    m_0 = "Generic message"

    # add asingle message to the channel
    requests.post(f"{url}/message/send", json={
        'token' : user1['token'],
        'channel_id' : c_id,
        'message' : m_0
    })


    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")


    assert messages.json()['start'] == 0
    assert messages.json()['end'] == -1
    assert messages.json()['messages'][0]['message'] == m_0


def test_single_message_priv(url, register_users):
    '''Retrieving messages from a private channel as an authorised user'''
    (user1,_,_) = register_users
    
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': False
        }).json())['channel_id']

    m_0 = "Generic message"

    # add asingle message to the channel
    requests.post(f"{url}/message/send", json={
        'token' : user1['token'],
        'channel_id' : c_id,
        'message' : m_0
    })


    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    assert messages.json()['start'] == 0
    assert messages.json()['end'] == -1
    assert messages.json()['messages'][0]['message'] == m_0



def test_60_messages(url, register_users):
    '''create a channel with 60 messages and retrieve the first 50'''
    (user1,_,_) = register_users
    
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': False
        }).json())['channel_id']

    m_0 = "m"

    for _ in range(60):
        requests.post(f"{url}/message/send", json={
            'token' : user1['token'],
            'channel_id' : c_id,
            'message' : m_0
        })
    
    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    assert messages.json()['start'] == start
    assert messages.json()['end'] == 50
    assert len(messages.json()['messages']) == 50


def test_30_messages(url, register_users):
    '''create a channel with  30 messages'''
    (user1,_,_) = register_users
    
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': "generic Channel", 
        'is_public': False
        }).json())['channel_id']

    m_0 = "m"

    for _ in range(30):
        requests.post(f"{url}/message/send", json={
            'token' : user1['token'],
            'channel_id' : c_id,
            'message' : m_0
        })
    
    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    assert messages.json()['start'] == start
    assert messages.json()['end'] == -1
    assert len(messages.json()['messages']) == 30



