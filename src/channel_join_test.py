# --------------------------- Tests for channel_join ---------------------------

import pytest
from error import InputError, AccessError
import auth
import channel
import channels
import other 

@pytest.fixture    
def register_users():
    other.clear()
    # user 1 is a global owner (1st person to sign up)
    user_1 = auth.auth_register('user1@gmail.com', '123456', 'Firstname', 'Surname')
    user_2 = auth.auth_register('user2@gmail.com', '123456', 'Firstname', 'Surname')
    user_3 = auth.auth_register('user3@gmail.com', '123456', 'Firstname', 'Surname')

    return (user_1, user_2, user_3)

def test_join_invalid_channel(register_users):
    '''
    Tests for invalid channels: users 1, 2 and 3 try to join a non-existent channel. 
    '''

    (user_1, user_2, user_3) = register_users

    with pytest.raises(InputError):
        channel.channel_join(user_1['token'], 0)
    with pytest.raises(InputError):
        channel.channel_join(user_2['token'], -1)
    with pytest.raises(InputError):
        channel.channel_join(user_3['token'], 1)

def test_join_invalid_token(register_users):
    '''
    Tests for invalid token: invalid token. 
    '''

    (user_1, _, _) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    token = user_1['token']

    with pytest.raises(AccessError):
        channel.channel_join(token + '1', pub_c_id_1)
    with pytest.raises(AccessError):
        channel.channel_join(token + ' ', pub_c_id_1)
    with pytest.raises(AccessError):
        channel.channel_join(' ', pub_c_id_1)

def test_join_non_global_owner(register_users):
    '''
    Tests for when the user is not a global owner: user 2 and 3 try to join
    channel_1 (private).
    '''

    (user_1, user_2, user_3) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', False)['channel_id']
    
    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], priv_c_id_1)
    with pytest.raises(AccessError):
        channel.channel_join(user_3['token'], priv_c_id_1)

def test_join_global_owner(register_users):
    '''
    Tests for when the user is a global owner: user 1 is a global owner and 
    joins channel_2 (private) and channel_3 (private).
    '''

    (user_1, user_2, user_3) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', False)['channel_id']
    priv_c_id_3 = channels.channels_create(user_3['token'], 'Channelname', False)['channel_id']
    
    assert(channel.channel_join(user_1['token'], priv_c_id_2) == {})
    assert(channel.channel_join(user_1['token'], priv_c_id_3) == {})

    owner_members = channel.channel_details(user_2['token'], priv_c_id_2)['owner_members']
    owner_u_ids = [owner['u_id'] for owner in owner_members]
    assert(user_1['u_id'] in owner_u_ids)
    
    all_members = channel.channel_details(user_3['token'], priv_c_id_3)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_1['u_id'] in member_u_ids)

def test_join_own_channel(register_users):
    '''
    Tests for when the user joins a channel they are already part of: user 1 and 
    2 rejoin their channels (no effect).
    '''

    (user_1, user_2, _) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', False)['channel_id']
    priv_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', False)['channel_id']
    
    assert(channel.channel_join(user_1['token'], priv_c_id_1) == {})
    assert(channel.channel_join(user_2['token'], priv_c_id_2) == {})

    all_members = channel.channel_details(user_1['token'], priv_c_id_1)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_1['u_id'] in member_u_ids)

    all_members = channel.channel_details(user_2['token'], priv_c_id_2)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_2['u_id'] in member_u_ids)

def test_join_success(register_users):
    '''
    Tests for join success: user 2 and 3 successfully join channel_1 (public).
    '''
    
    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']

    assert(channel.channel_join(user_2['token'], pub_c_id_1) == {})
    assert(channel.channel_join(user_3['token'], pub_c_id_1) == {})

    all_members = channel.channel_details(user_1['token'], pub_c_id_1)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_2['u_id'] in member_u_ids)
    assert(user_3['u_id'] in member_u_ids)
