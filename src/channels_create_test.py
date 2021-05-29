import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create
from channel import channel_details, channel_join
from other import clear

@pytest.fixture
def token():
    auth_register('email@filler.com', 'fillerpass', 'firstfiller', 'lastfiller')
    new_token = auth_register('email@something.com', 'password', 'first', 'last')['token']
    new_token2 = auth_register('2email@something.com', '2password', '2first', '2last')['token']
    return (new_token, new_token2)

@pytest.fixture(autouse=True)
def clear_only():
    clear()
    
def test_channels_create_invalid_token():
    """ Test for invalid token """
    with pytest.raises(AccessError):
        channels_create('not_a_token', 'some_name', True)

def test_channels_create_return_type(token):
    """ Test returns channel_id wrapped in dictionary """
    channel = channels_create(token[0], 'channel1', False)
    assert('channel_id' in channel.keys())
    assert(len(channel) == 1)

def test_channels_create_channel_name(token):
    """ Test channel name is properly stored """
    channel_id = channels_create(token[0], 'channel1', False)['channel_id']
    channel_info = channel_details(token[0], channel_id)
    assert(channel_info['name'] == 'channel1')

def test_channels_create_is_private(token):
    """ Test is_public is set to false """
    channel_id = channels_create(token[0], 'channel1', False)['channel_id']
    with pytest.raises(AccessError):
        channel_join(token[1], channel_id)

def test_channels_create_is_public(token):
    """ Test is_public is set to true """
    channel_id = channels_create(token[0], 'channel1', True)['channel_id']
    assert(channel_join(token[1], channel_id) == {})
        
def test_channels_create_name_more_than_20_char(token):
    """ Test error for when name is longer than 20 characters """
    with pytest.raises(InputError):
        channels_create(token[0], 'nameislongerthantwent', True)
