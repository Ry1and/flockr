import requests
import json
from error import AccessError, InputError
import pytest
from server_test_fixtures import url, register_users,create_channels
from datetime import datetime as dt, timezone


def test_sanity(url):
    '''Check if the server is running ''' 
    assert url.startswith("http")


def test_invalid_token(url, create_channels):
    ''' raise an access error if the token is invalid'''
    (pub_channel_id,_,_,_) = create_channels
    message = "Generic message"
    send = requests.post(f"{url}/message/send", json={
        'token' : 'invalidtoken',
        'channel_id' : pub_channel_id,
        'message' : message
    })


    assert send.status_code == AccessError.code


def test_invalid_channel(url, register_users):
    '''when the user tries to send a message to a channel that doesnt exist'''
    (user1,_,_) = register_users
    
    message = "generic message"
    send = requests.post(f"{url}/message/send",json={
        'token' : user1['token'],
        'channel_id' : -42,
        'message' : message
    })

    assert send.status_code == InputError.code


def test_not_member(url, register_users):
    '''When a user tries to send a message to a channel they are not a member of '''
    (user1,user2,_) = register_users
    
    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': True
        }).json())['channel_id']

    message = "generic message"
    send = requests.post(f"{url}/message/send",json={
        'token' : user2['token'],
        'channel_id' : c_id,
        'message' : message
    })

    assert send.status_code == AccessError.code


def test_message_too_long(url, register_users):
    ''' When the message is >1000 characters'''

    (user1,_,_) = register_users

    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': True
        }).json())['channel_id']
    
    message = "a" * 1002
    send = requests.post(f"{url}/message/send",json={
        'token' : user1['token'],
        'channel_id' : c_id,
        'message' : message
    })

    assert send.status_code == InputError.code


def test_send_1_message(url, register_users):
    '''
    Add a single message to a public channel,
    check if the message was sent,if the returned message id matches the one 
    of the message that was sent, check if the send_time matches and if the
    time created matches the send time
    '''

    (user1,_,_) = register_users

    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create', json = {
        'token': user1['token'],
        'name': c_name, 
        'is_public': True
        }).json())['channel_id']
    
    m_0 = "hello"
    
    send = requests.post(f"{url}/message/send",json={
        'token' : user1['token'],
        'channel_id' : c_id,
        'message' : m_0
    })
    send_time = dt.utcnow()
    send_time = send_time.replace(tzinfo=timezone.utc).timestamp()

    margin = 0.001

    message_id = send.json()['message_id']

    start = 0
    messages = requests.get(f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={start}")

    message = messages.json()['messages'][start]

    

    assert (message['time_created'] - send_time < margin)
    assert m_0 == message['message']
    assert message_id == message['message_id']
    assert user1['u_id'] == message['u_id']
