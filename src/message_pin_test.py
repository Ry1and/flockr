import pytest
from error import InputError, AccessError
from message import message_send, message_pin
from channel import channel_join
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

def test_message_pin_invalid_token():
    """ Test invalid token """
    with pytest.raises(AccessError):
        message_pin('not_a_token', 0)

def test_message_pin_message_does_not_exist(setup):
    """ Test InputError for message does not exist """
    (_, channel_owner_token, normal_token, _, _, _) = setup
    with pytest.raises(InputError):
        message_pin(channel_owner_token, 0)
        message_pin(normal_token, 0)

def test_message_pin_not_member_of_channel(setup):
    """ Test AccessError for not member of the channel """
    (_, channel_owner_token, normal_token, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'test_message')['message_id']
    with pytest.raises(AccessError):
        message_pin(normal_token, message_id)

def test_message_pin_not_channel_owner(setup):
    """ Test AccessError for when user is not channel owner """
    (_, _, normal_token, channel_id1, _, _) = setup
    channel_join(normal_token, channel_id1)
    message_id = message_send(normal_token, channel_id1, 'test_message')['message_id']
    with pytest.raises(AccessError):
        message_pin(normal_token, message_id)

def test_message_pin_pinned_successfully_AND_message_already_pinned(setup):
    """ Test normal use case of pin and also InputError for when message is already pinned """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'test_message')['message_id']
    message_pin(channel_owner_token, message_id)
    with pytest.raises(InputError):
        message_pin(channel_owner_token, message_id)

def test_message_pin_return_type(setup):
    """ Test return type for message_pin """
    (_, channel_owner_token, _, channel_id1, _, _) = setup
    message_id = message_send(channel_owner_token, channel_id1, 'test_message')['message_id']
    assert message_pin(channel_owner_token, message_id) == {}
