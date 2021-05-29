import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create, channels_listall, channels_list
from other import clear

@pytest.fixture
def clist():
    auth_register('email@filler.com', 'fillerpass', 'firstfiller', 'lastfiller')
    token1 = auth_register('email@something.com', 'password', 'first', 'last')['token']
    token2 = auth_register('2email@something.com', '2password', '2first', '2last')['token']
    channel_id1 = channels_create(token1, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token1, 'channel2', True)['channel_id']
    channel_id3 = channels_create(token2, 'channel3', True)['channel_id']
    info_tuple = (token1, token2, channel_id1, channel_id2, channel_id3)
    return info_tuple

@pytest.fixture(autouse=True)
def clear_only():
    clear()

def test_channels_list_invalid_token():
    """ Test for invalid token """
    with pytest.raises(AccessError):
        channels_list('not_a_token')

def test_channels_list_return_type(clist):
    """ Test return type fields are correct """
    ch_list = channels_list(clist[0])
    assert all(x in ch_list['channels'][0].keys() for x in ['channel_id', 'name'])
    assert len(ch_list['channels'][0]) == 2

def test_channels_list_with_permission(clist):
    """ Test listing channels that the user is part of """
    ch_list = channels_list(clist[0])
    ch_listall = channels_listall(clist[0])
    assert ch_list['channels'][0] in ch_listall['channels']
    assert ch_list['channels'][1] in ch_listall['channels']

def test_channels_list_without_permission(clist):
    """ Test listing channels that the user is not a part of """
    ch_list = channels_list(clist[0])
    channel_name_list = [channel['name'] for channel in ch_list['channels']]
    assert len(ch_list['channels']) == 2
    assert 'channel3' not in channel_name_list

def test_channels_list_empty_channel_list():
    """ Test return value when there are no existing channels """
    token = auth_register('email@something.com', 'password', 'first', 'last')['token']
    assert channels_list(token) == {'channels':[]}
    
