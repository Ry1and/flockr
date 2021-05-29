import pytest
import message
import channel
import channels
import auth
from error import AccessError, InputError
import other

'''Tests for message_unreact function in message.py '''

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
        message.message_unreact('invalidtoken', message_id, REACT_ID)

def test_invalid_message_id(initialise):
    '''
    message_id is not a valid message within a channel that the authorised user has joined
    '''
    (user0, _, _, _) = initialise

    invalid_message_id = -42

    with pytest.raises(InputError):
        message.message_unreact(user0['token'], invalid_message_id, REACT_ID)


def test_invalid_react_id(initialise):
    '''react_id is not a valid React ID. The only valid react ID the frontend has is 1'''

    (user0, _, _, message_id) = initialise

    with pytest.raises(InputError):
        message.message_unreact(user0['token'], message_id, -42)



def test_not_reacted(initialise):
    '''user0 tries to unreact to a message user1 has reacted to''' 

    (user0, user1, _, message_id) = initialise

    message.message_react(user1['token'], message_id, REACT_ID)

    with pytest.raises(InputError):
        message.message_unreact(user0['token'], message_id, REACT_ID)


def test_react_unreact_one(initialise):
    '''
    user0 reacts to test_message and then unreacts to it
    '''

    (user0, _, channel_id, message_id) = initialise

    #user0 reacts to the test message
    message.message_react(user0['token'], message_id, REACT_ID)

    test_react = channel.channel_messages(user0['token'], channel_id, 0)['messages'][0]['reacts']
    
    assert test_react[0]['react_id'] == REACT_ID
    assert test_react[0]['is_this_user_reacted'] == True
    assert len(test_react[0]['u_ids']) == 1

    # user0 unreacts.
    message.message_unreact(user0['token'], message_id, REACT_ID)
    
    test_react = channel.channel_messages(user0['token'], channel_id, 0)['messages'][0]['reacts']
    
    assert test_react[0]['react_id'] == REACT_ID
    assert test_react[0]['is_this_user_reacted'] == False
    assert len(test_react[0]['u_ids']) == 0

def test_react_unreact_two(initialise):
    ''''''

    (user0, user1, channel_id, message_id) = initialise
    channel.channel_join(user1['token'], channel_id)

    message.message_react(user0['token'], message_id, REACT_ID)
    message.message_react(user1['token'], message_id, REACT_ID)

    test_react_0 = channel.channel_messages(user0['token'], channel_id, 0)['messages'][0]['reacts']
    test_react_1 = channel.channel_messages(user1['token'], channel_id, 0)['messages'][0]['reacts']
    
    assert test_react_0[0]['react_id'] == REACT_ID
    assert test_react_0[0]['is_this_user_reacted'] == True
    assert len(test_react_0[0]['u_ids']) == 2

    assert test_react_1[0]['react_id'] == REACT_ID
    assert test_react_1[0]['is_this_user_reacted'] == True
    assert len(test_react_1[0]['u_ids']) == 2


    # user0 unreacts.
    message.message_unreact(user0['token'], message_id, REACT_ID)
    
    test_react_0 = channel.channel_messages(user0['token'], channel_id, 0)['messages'][0]['reacts']
    
    assert test_react_0[0]['react_id'] == REACT_ID
    assert test_react_0[0]['is_this_user_reacted'] == False
    assert len(test_react_0[0]['u_ids']) == 1

    message.message_unreact(user1['token'], message_id, REACT_ID)

    test_react_1 = channel.channel_messages(user1['token'], channel_id, 0)['messages'][0]['reacts']

    assert test_react_0[0]['react_id'] == REACT_ID
    assert test_react_0[0]['is_this_user_reacted'] == False
    assert len(test_react_0[0]['u_ids']) == 0














