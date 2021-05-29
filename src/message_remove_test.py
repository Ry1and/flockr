import pytest
from error import InputError, AccessError
from message import message_remove, message_send
from channel import channel_join, channel_messages
from channels import channels_create
from auth import auth_register
from other import clear

@pytest.fixture()
def setup():
    global_token = auth_register('email@filler.com', 'fillerpass', 'firstfiller', 'lastfiller')['token']
    channel_owner_token = auth_register('1email@something.com', '1password', '1first', '1last')['token']
    normal_token = auth_register('2email@something.com', '2password', '2first', '2last')['token']
    channel_id1 = channels_create(channel_owner_token, 'channel1', True)['channel_id']
    channel_id2 = channels_create(channel_owner_token, 'channel2', True)['channel_id']
    channel_id3 = channels_create(channel_owner_token, 'channel3', True)['channel_id']
    return (global_token, channel_owner_token, normal_token, channel_id1, channel_id2, channel_id3)

@pytest.fixture(autouse=True)
def clear_only():
    clear()

def test_message_remove_invalid_token():
    """ Test invalid token """
    with pytest.raises(AccessError):
        message_remove('not_a_token', 0)

def test_message_remove_return_value(setup):
    """ Test return value is {} """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'stub_message')['message_id']
    assert(message_remove(channel_owner_token, message_id) == {})

def test_message_remove_not_authorised_not_owner(setup):
    """
    Test case for user not a global owner, not a channel owner, not the user
    that sent the message.
    """
    (_, channel_owner_token, normal_token, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'stub_message')['message_id']
    with pytest.raises(AccessError):
        message_remove(normal_token, message_id)

def test_message_remove_only_global_owner(setup):
    """ Test case for being a global owner only """
    (global_token, channel_owner_token, _, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'stub_message')['message_id']
    message_remove(global_token, message_id)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'] == [])

def test_message_remove_only_channel_owner(setup):
    """ Test case for being a channel owner only """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'stub_message')['message_id']
    message_remove(channel_owner_token, message_id)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'] == [])

def test_message_remove_only_authorised_user(setup):
    """ Test case for being the user who sent the message only """
    (_, channel_owner_token, normal_token, channel_id1, _, _) = setup
    channel_join(normal_token, channel_id1)
    message_id = message_send(normal_token, channel_id1, 'stub_message')['message_id']
    message_remove(normal_token, message_id)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'] == [])

def test_message_remove_multiple_channels(setup):
    """ Simple test for removing messages from multiple channels """
    (_, channel_owner_token, _, channel_id1, channel_id2, channel_id3) = setup
    message_id1 = message_send(channel_owner_token, channel_id1, 'stub_message1')['message_id']
    message_id2 = message_send(channel_owner_token, channel_id1, 'stub_message2')['message_id']
    message_id3 = message_send(channel_owner_token, channel_id2, 'stub_message3')['message_id']
    message_id4 = message_send(channel_owner_token, channel_id2, 'stub_message4')['message_id']
    message_id5 = message_send(channel_owner_token, channel_id3, 'stub_message5')['message_id']
    message_id6 = message_send(channel_owner_token, channel_id3, 'stub_message6')['message_id']
    message_remove(channel_owner_token, message_id2)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][0]['message_id'] == message_id1)
    message_remove(channel_owner_token, message_id3)
    assert(channel_messages(channel_owner_token, channel_id2, 0)['messages'][0]['message_id'] == message_id4)
    message_remove(channel_owner_token, message_id5)
    assert(channel_messages(channel_owner_token, channel_id3, 0)['messages'][0]['message_id'] == message_id6)

def test_message_remove_some_channels_empty(setup):
    """ Test for removing messages when some channels do not have any messages """
    (_, channel_owner_token, _, channel_id1, _, channel_id3) = setup
    message_id1 = message_send(channel_owner_token, channel_id1, 'stub_message1')['message_id']
    message_id2 = message_send(channel_owner_token, channel_id1, 'stub_message2')['message_id']
    message_id3 = message_send(channel_owner_token, channel_id3, 'stub_message3')['message_id']
    message_id4 = message_send(channel_owner_token, channel_id3, 'stub_message4')['message_id']
    message_remove(channel_owner_token, message_id1)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][0]['message_id'] == message_id2)
    message_remove(channel_owner_token, message_id4)
    assert(channel_messages(channel_owner_token, channel_id3, 0)['messages'][0]['message_id'] == message_id3)

def test_message_remove_multiple_messages_same_channel(setup):
    """ Test for removing multiple messages from the same channel """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id1 = message_send(channel_owner_token, channel_id1, 'stub_message1')['message_id']
    message_id2 = message_send(channel_owner_token, channel_id1, 'stub_message2')['message_id']
    message_id3 = message_send(channel_owner_token, channel_id1, 'stub_message3')['message_id']
    message_id4 = message_send(channel_owner_token, channel_id1, 'stub_message4')['message_id']
    message_remove(channel_owner_token, message_id2)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][0]['message_id'] == message_id4)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][1]['message_id'] == message_id3)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][2]['message_id'] == message_id1)
    message_remove(channel_owner_token, message_id4)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][0]['message_id'] == message_id3)
    assert(channel_messages(channel_owner_token, channel_id1, 0)['messages'][1]['message_id'] == message_id1)

def test_message_remove_message_does_not_exist(setup):
    """ 
    Test for removing a message that does not exist from a channel 
    that does exist and has existing messages
    """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id1 = message_send(channel_owner_token, channel_id1, 'stub_message1')['message_id']
    with pytest.raises(InputError):
        message_remove(channel_owner_token, message_id1 + 1)

def test_message_remove_no_channels_exist():
    """ Test for removing message when no channels exist """
    global_token = auth_register('email@filler.com', 'fillerpass', 'firstfiller', 'lastfiller')['token']
    with pytest.raises(InputError):
        message_remove(global_token, 10)

