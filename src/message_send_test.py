import pytest
import channel
import channels
from message import message_send
import auth
from error import AccessError, InputError
import other

'''Tests for the message_send function in message.py '''


@pytest.fixture
def initialise():
    other.clear()
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    user1 = auth.auth_register('name1@gmail.com', 'password1', 'f_name1', 'l_name1')
    
    channel_id = channels.channels_create(user0['token'], "generic channel", True)['channel_id']
    
    return (user0, user1, channel_id)


def test_invalid_token(initialise):
    (_, _, channel_id) = initialise
    
    with pytest.raises(AccessError):
        message_send('invalidtoken1', channel_id,"hello")

def test_valid_channel(initialise):
    (user0, _, _) = initialise
    with pytest.raises(InputError):
        message_send(user0['token'], -42, "world")


def test_send_1000(initialise):
    ''' when message is more than 1000 characters, raise an Input error'''
    (user0, _, channel_id) = initialise
    message0 = "a" * 1001 
    
    with pytest.raises(InputError):
        message_send(user0['token'], channel_id, message0)


def test_not_member(initialise):
    ''' when a user, who is not a member of a channel tries
        to send a message in that channel
    '''
    (_, user1, channel_id) = initialise
    message0 = "I am not a member of this channel"
    with pytest.raises(AccessError):
        message_send(user1['token'], channel_id, message0)


 
def test_basic(initialise):
    ''' 
    basic test: adding a message to a channel with no messages
    when user is channel owner 
    '''
    (user0, _, channel_id) = initialise
    
    message0 = "Hello Channel"
    message_send(user0['token'],channel_id,message0)
    data = channel.channel_messages(user0['token'], channel_id, 0)
    
    assert (data['messages'][0]['message'] == message0)

def test_not_owner(initialise):
    ''' 
    basic test: sending a message to a channel with no previous messages
    where the user is just a channel member 
    '''
    (user0, user1, channel_id) = initialise
    message0 = "Hello Channel"
    channel.channel_join(user1['token'], channel_id)

    message_send(user1['token'],channel_id,message0)
    data = channel.channel_messages(user0['token'], channel_id, 0)

    assert (data['messages'][0]['message'] == message0)



def test_two_messages(initialise):
    ''' 
        check to see if two messages from two users,
        when sent, are added to the channel 
    ''' 
    (user0, user1, channel_id) = initialise
    message0 = "This is message 1"
    message1 = "This is message 2"
    channel.channel_join(user1['token'], channel_id)

    message_send(user0['token'],channel_id,message0)
    message_send(user1['token'], channel_id, message1)

    data = channel.channel_messages(user0['token'], channel_id, 0)
    assert (data['messages'][0]['message'] == message1) 
    assert (data['messages'][1]['message'] == message0)
