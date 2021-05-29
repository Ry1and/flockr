import pytest
import message
import channel
import channels
import auth
from error import AccessError, InputError
import other
from datetime import datetime as dt, timezone, time, timedelta
import time

'''Tests for message_send_later function in message.py'''


@pytest.fixture
def initialise():
    other.clear()
    
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    user1 = auth.auth_register('name1@gmail.com', 'password1', 'f_name1', 'l_name1')

    channel_id = channels.channels_create(user0['token'], "generic channel", True)['channel_id']

    time_sent = dt.utcnow() + timedelta(seconds=20)
    time_sent = int(time_sent.replace(tzinfo=timezone.utc).timestamp())
    
    return (user0, user1, channel_id, time_sent)


def test_invalid_token(initialise):
    (_, _, channel_id, time_sent) = initialise

    m = "test message"
    
    
    with pytest.raises(AccessError):
        message.message_sendlater('invalid', channel_id, m, time_sent)


def test_invalid_channel_id(initialise):
    '''Channel ID doesnt exist'''
    (user0, _, _, time_sent) = initialise

    m = "test message"
    
    
    with pytest.raises(InputError):
        message.message_sendlater(user0['token'], -42, m, time_sent)

def test_send_later_1000(initialise):
    '''The message is too long'''
    (user0, _, channel_id, time_sent) = initialise


    m = "a" * 1001
    
    with pytest.raises(InputError):
        message.message_sendlater(user0['token'], channel_id, m, time_sent)


def test_invalid_time(initialise):
    '''The send_time is invalid'''
    (user0, _, channel_id, _) = initialise

    m = "test message"
    time_sent = dt.utcnow() - timedelta(hours=1)
    time_sent = int(time_sent.replace(tzinfo=timezone.utc).timestamp())

    with pytest.raises(InputError):
        message.message_sendlater(user0['token'], channel_id, m, time_sent)



def test_not_member(initialise):
    '''The authorised user is not a member of the channel'''
    (_, user1, channel_id, time_sent) = initialise

    m = "test message"
    
    with pytest.raises(AccessError):
        message.message_sendlater(user1['token'], channel_id, m, time_sent)


def test_send_20_sec(initialise):
    '''send a message after 20 seconds'''
    (user0, _, channel_id, time_sent) = initialise

    m = "hello"

    message.message_sendlater(user0['token'], channel_id, m, time_sent)

    time.sleep(25)

    margin = 1
    
    sent_message = channel.channel_messages(user0['token'], channel_id,0)['messages'][0]
    assert (sent_message['time_created'] - time_sent) < margin
    assert sent_message['message'] == m

def test_send_two(initialise):
    '''
    send a message after 20 seconds and another message
    after another 10 seconds
    '''

    (user0, user1, channel_id, _) = initialise

    channel.channel_invite(user0['token'], channel_id, user1['u_id'])

    m_0 = "hello"
    time_sent_0 = dt.utcnow() + timedelta(seconds=20)
    time_sent_0 = int(time_sent_0.replace(tzinfo=timezone.utc).timestamp())

    m_1 = "world"
    time_sent_1 = dt.utcnow() + timedelta(seconds=30)
    time_sent_1 = int(time_sent_1.replace(tzinfo=timezone.utc).timestamp())

    message.message_sendlater(user1['token'], channel_id, m_1, time_sent_1)
    message.message_sendlater(user0['token'], channel_id, m_0, time_sent_0)
    

    time.sleep(35)

    margin = 1

    sent_message_1 = channel.channel_messages(user0['token'], channel_id,0)['messages'][0]
    sent_message_0 = channel.channel_messages(user0['token'], channel_id,0)['messages'][1]

    assert sent_message_0['time_created'] - time_sent_0 < margin
    assert sent_message_0['message'] == m_0
    assert sent_message_1['time_created'] - time_sent_1 < margin
    assert sent_message_1['message'] == m_1


