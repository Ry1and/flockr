import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels


@pytest.fixture
def initialise_unreact(url, register_users):
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


def test_invalid_token(initialise_unreact):
    '''Test with an invalid token'''
    (url, _, _, _, m_id, react_id) = initialise_unreact

    unreact = requests.post(f"{url}/message/unreact",
                            json={
                                'token': 'invalid',
                                'message_id': m_id,
                                'react_id': react_id
                            })

    assert unreact.status_code == AccessError.code


def test_invalid_message_id(initialise_unreact):
    '''message_id is not a valid message within a channel that the authorised user has joined'''
    (url, user0, _, _, _, react_id) = initialise_unreact

    unreact = requests.post(f"{url}/message/unreact",
                            json={
                                'token': user0['token'],
                                'message_id': -42,
                                'react_id': react_id
                            })

    assert unreact.status_code == InputError.code


def test_invalid_react_id(initialise_unreact):
    '''react_id is not a valid React ID. The only valid react ID the frontend has is 1'''
    (url, user0, _, _, m_id, _) = initialise_unreact
    unreact = requests.post(f"{url}/message/unreact",
                            json={
                                'token': user0['token'],
                                'message_id': m_id,
                                'react_id': -42
                            })

    assert unreact.status_code == InputError.code


def test_not_reacted(initialise_unreact):
    (url, user0, _, _, m_id, react_id) = initialise_unreact
    unreact = requests.post(f"{url}/message/unreact",
                            json={
                                'token': user0['token'],
                                'message_id': m_id,
                                'react_id': react_id
                            })

    assert unreact.status_code == InputError.code


def test_unreact_one(initialise_unreact):
    (url, user0, _, c_id, m_id, react_id) = initialise_unreact

    requests.post(f"{url}/message/react",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    requests.post(f"{url}/message/unreact",
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
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 0

def test_unreact_two(initialise_unreact):
    (url, user0, user1, c_id, m_id, react_id) = initialise_unreact

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

    requests.post(f"{url}/message/unreact",
                  json={
                      'token': user0['token'],
                      'message_id': m_id,
                      'react_id': react_id
                  })

    messages = requests.get(
        f"{url}/channel/messages?token={user0['token']}&channel_id={c_id}&start={0}"
    )

    test_react = messages.json()['messages'][0]['reacts']


    assert test_react[0]['react_id'] == react_id
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 1

    requests.post(f"{url}/message/unreact",
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
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 0


    




    
    


    

