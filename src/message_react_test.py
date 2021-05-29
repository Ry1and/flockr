import pytest
import message
import channel
import channels
import auth
from error import AccessError, InputError
import other

'''Tests for message_react function in message.py '''

REACT_ID = 1

@pytest.fixture
def initialise():
    other.clear()
    
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    user1 = auth.auth_register('name1@gmail.com', 'password1', 'f_name1', 'l_name1')

    channel_id = channels.channels_create(user0['token'], "generic channel", True)['channel_id']

    message_id = message.message_send(user0['token'], channel_id, "Test message")['message_id']

    return (user0, user1, channel_id, message_id)



def test_invalid_token(initialise):
    (_, _, _, message_id) = initialise

    with pytest.raises(AccessError):
        message.message_react('invalidtoken', message_id, REACT_ID)

def test_invalid_message_id(initialise):
    '''
    message_id is not a valid message within a channel that the authorised user has joined
    '''
    (user0, _, _, _) = initialise

    invalid_message_id = -42

    with pytest.raises(InputError):
        message.message_react(user0['token'], invalid_message_id, REACT_ID)


def test_invalid_react_id(initialise):
    '''react_id is not a valid React ID. The only valid react ID the frontend has is 1'''

    (user0, _, _, message_id) = initialise

    with pytest.raises(InputError):
        message.message_react(user0['token'], message_id, -42)



def test_already_reacted(initialise):
    '''Message with ID message_id already contains an active React 
    with ID react_id from the authorised user''' 

    (user0, _, _, message_id) = initialise

    message.message_react(user0['token'], message_id, REACT_ID)

    with pytest.raises(InputError):
        message.message_react(user0['token'], message_id, REACT_ID)


def test_you_reacted_one_(initialise):
    '''When user0 react to the test message sent by user0, message retrieved by user0 '''
    (user0, _, channel_id, message_id) = initialise

    # user0 reacts to the test_message
    message.message_react(user0['token'], message_id, REACT_ID)

    test_react = channel.channel_messages(user0['token'], channel_id, 0)['messages'][0]['reacts']
    print (test_react)
    
    assert test_react[0]['react_id'] == REACT_ID
    assert test_react[0]['is_this_user_reacted'] == True
    assert len(test_react[0]['u_ids']) == 1

def test_user_reacted_one(initialise):
    '''When user0 react to the test message sent by user0, message retrieved by user1'''
    (user0, user1, channel_id, message_id) = initialise

    message.message_react(user0['token'], message_id, REACT_ID)

    channel.channel_join(user1['token'], channel_id)

    test_react = channel.channel_messages(user1['token'], channel_id, 0)['messages'][0]['reacts']
    
    assert test_react[0]['react_id'] == REACT_ID
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 1


def test_reacted_two(initialise):
    '''When two user0 and user1 react to the test message, message retrieved by user0'''
    (user0, user1, channel_id, message_id) = initialise

    message.message_react(user0['token'], message_id, REACT_ID)

    channel.channel_join(user1['token'], channel_id)

    message.message_react(user1['token'], message_id, REACT_ID)

    test_react = channel.channel_messages(user1['token'], channel_id, 0)['messages'][0]['reacts']

    assert test_react[0]['react_id'] == REACT_ID
    assert test_react[0]['is_this_user_reacted'] == True
    assert len(test_react[0]['u_ids']) == 2

