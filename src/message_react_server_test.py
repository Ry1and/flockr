import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels


@pytest.fixture
def initialise_react(url, register_users):
    (user0, user1, _) = register_users

    #user0 creates a public channel
    c_name = "public_channel"
    c_id = (requests.post(f'{url}/channels/create',
                          json={
                              'token': user0['token'],
                              'name': c_name,
                              'is_public': True
                          }).json())['channel_id']

    #user1 joins the channel
    requests.post(f"{url}/channel/join",
                  json={
                      'token': user1['token'],
                      'channel_id': c_id
                  })

    #user0 sends a message
    message = "hello world"
    m_id = requests.post(f"{url}/message/send",
                         json={
                             'token': user0['token'],
                             'channel_id': c_id,
                             'message': message
                         })
    payload = m_id.json()
    m_id = payload['message_id']
    react_id = 1

    return (url, user0, user1, c_id, m_id, react_id)


def test_sanity(url):
    '''Test to check if the server is running '''
    assert url.startswith("http")


def test_invalid_token(initialise_react):
    '''Test with an invalid token'''
    (url, _, _, _, m_id, react_id) = initialise_react

    react = requests.post(f"{url}/message/react",
                          json={
                              'token': 'invalid',
                              'message_id': m_id,
                              'react_id': react_id
                          })

    assert react.status_code == AccessError.code


def test_invalid_message_id(initialise_react):
    '''message_id is not a valid message within a channel that the authorised user has joined'''
    (url, user0, _, _, _, react_id) = initialise_react

    react = requests.post(f"{url}/message/react",
                          json={
                              'token': user0['token'],
                              'message_id': -42,
                              'react_id': react_id
                          })

    assert react.status_code == InputError.code


def test_invalid_react_id(initialise_react):
    '''react_id is not a valid React ID. The only valid react ID the frontend has is 1'''
    (url, user0, _, _, m_id, _) = initialise_react
    react = requests.post(f"{url}/message/react",
                          json={
                              'token': user0['token'],
                              'message_id': m_id,
                              'react_id': -42
                          })

    assert react.status_code == InputError.code


def test_already_reacted(initialise_react):
    '''
    Message with ID message_id already contains an active React 
    with ID react_id from the authorised user
    '''

    (url, user0, _, _, m_id, react_id) = initialise_react

    requests.post(f"{url}/message/react",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    react = requests.post(f"{url}/message/react",
                          json={
                              'token': user0['token'],
                              'message_id': m_id,
                              'react_id': react_id
                          })

    assert react.status_code == InputError.code


def test_you_reacted_one(initialise_react):
    '''When user0 react to the test message sent by user0, message retrieved by user0 '''
    (url, user0, _, c_id, m_id, react_id) = initialise_react

    requests.post(f"{url}/message/react",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    messages = requests.get(
        f"{url}/channel/messages?token={user0['token']}&channel_id={c_id}&start={0}"
    )

    # get the rect_status of the test message
    test_react = messages.json()['messages'][0]['reacts']

    assert test_react[0]['react_id'] == react_id
    assert test_react[0]['is_this_user_reacted'] == True
    assert len(test_react[0]['u_ids']) == 1


def test_user_reacted_one(initialise_react):
    '''When user0 react to the test message sent by user0, message retrieved by user1'''
    (url, user0, user1, c_id, m_id, react_id) = initialise_react

    requests.post(f"{url}/message/react",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    messages = requests.get(
        f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={0}"
    )

    test_react = messages.json()['messages'][0]['reacts']

    assert test_react[0]['react_id'] == react_id
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 1


def test_reacted_two(initialise_react):
    '''When two user0 and user1 react to the test message, message retrieved by user0'''
    (url, user0, user1, c_id, m_id, react_id) = initialise_react

    requests.post(f"{url}/message/react",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    requests.post(f"{url}/message/react",
                  json={
                      'token': user1['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    messages = requests.get(
        f"{url}/channel/messages?token={user1['token']}&channel_id={c_id}&start={0}"
    )

    test_react = messages.json()['messages'][0]['reacts']

    assert test_react[0]['react_id'] == react_id
    assert test_react[0]['is_this_user_reacted'] == True
    assert len(test_react[0]['u_ids']) == 2
