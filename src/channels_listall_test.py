import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create, channels_listall, channels_list
from channel import channel_details, channel_join
from other import clear

@pytest.fixture
def clistall():
    auth_register('email@filler.com', 'fillerpass', 'firstfiller', 'lastfiller')
    token1 = auth_register('email@something.com', 'password', 'first', 'last')['token']
    token2 = auth_register('2email@something.com', '2password', '2first', '2last')['token']
    channel_id1 = channels_create(token1, 'channel1', True)['channel_id']
    channel_id2 = channels_create(token2, 'channel2', True)['channel_id']
    info_tuple = (token1, token2, channel_id1, channel_id2)
    return info_tuple

@pytest.fixture(autouse=True)
def clear_only():
    clear()
    
def test_channels_listall_invalid_token():
    """ Test invalid token """
    with pytest.raises(AccessError):
        channels_listall('not_a_token')

def test_channels_listall_return_type(clistall):
    """ Test the correct fields are being returned """
    ch_listall = channels_listall(clistall[0])
    assert all(x in ch_listall['channels'][0].keys() for x in ['channel_id', 'name'])
    assert len(ch_listall['channels'][0]) == 2

def test_channels_listall_different_channel_owners(clistall):
    """ Test all channels are listed despite different channel owners """
    ch_listall = channels_listall(clistall[0])
    channel_id_list = [channel['channel_id'] for channel in ch_listall['channels']]
    channel_name_list = [channel['name'] for channel in ch_listall['channels']]
    assert clistall[2] in channel_id_list
    assert clistall[3] in channel_id_list
    assert 'channel1' in channel_name_list
    assert 'channel2' in channel_name_list

def test_channels_listall_no_channels():
    """ Test return type when there are no channels """
    token = auth_register('email@something.com', 'password', 'first', 'last')['token']
    assert channels_listall(token) == {'channels':[]}
    
