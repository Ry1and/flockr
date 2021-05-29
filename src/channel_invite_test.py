# -------------------------- Tests for channel_invite --------------------------

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

def test_invite_invalid_channel(register_users):
    '''
    Tests for invalid channels: user 1 invites user 2 to a non-existent channel. 
    '''

    (user_1, user_2, _) = register_users

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], 0, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], -1, user_2['u_id'])
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], 2, user_2['u_id'])

def test_invite_invalid_token(register_users):
    '''
    Tests for invalid token: invalid token. 
    '''

    (user_1, user_2, _) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    token = user_1['token']

    with pytest.raises(AccessError):
        channel.channel_invite(token + '1', pub_c_id_1, user_2['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(token + ' ', pub_c_id_1, user_2['u_id'])
    with pytest.raises(AccessError):
        channel.channel_invite(' ', pub_c_id_1, user_2['u_id'])
 
def test_invite_invalid_user(register_users):
    '''
    Tests for invalid users: user 1 invites a non-existent user to channel_1 (public). 
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    u_id_1 = user_1['u_id'] + user_2['u_id'] + user_3['u_id']
    u_id_2 = -user_1['u_id'] - user_2['u_id'] - user_3['u_id']

    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], pub_c_id_1, u_id_1)
    with pytest.raises(InputError):
        channel.channel_invite(user_1['token'], pub_c_id_1, u_id_2)

def test_invite_others_non_member(register_users):
    '''
    Tests for when a user who is inviting others is not a member of the channel: 
    user 2 invites user 3 to channel_1 (public), and vice versa.
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], pub_c_id_1, user_3['u_id']) 
    with pytest.raises(AccessError):
        channel.channel_invite(user_3['token'], pub_c_id_1, user_2['u_id'])

def test_invite_self_non_member(register_users):
    '''
    Tests for when a user who is inviting themselves is not a member of the channel: 
    user 2 and 3 invite themselves to channel_1 (public). 
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_invite(user_2['token'], pub_c_id_1, user_2['u_id']) 
    with pytest.raises(AccessError):
        channel.channel_invite(user_3['token'], pub_c_id_1, user_3['u_id'])

def test_invite_in_channel(register_users):
    '''
    Tests for when a user who is already in a channel invites themselves: user 1 
    invites themselves to channel_1 (no effect).
    '''

    (user_1, _, _) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', False)['channel_id']

    assert(channel.channel_invite(user_1['token'], priv_c_id_1, user_1['u_id']) == {})
    all_members = channel.channel_details(user_1['token'], priv_c_id_1)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_1['u_id'] in member_u_ids)

def test_invite_others_public(register_users):
    '''
    Tests for invitation success: user 1 succesfully adds user 2 and 3 to 
    channel_1 (public).  
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']

    assert(channel.channel_invite(user_1['token'], pub_c_id_1, user_2['u_id']) == {})
    assert(channel.channel_invite(user_1['token'], pub_c_id_1, user_3['u_id']) == {})

    all_members = channel.channel_details(user_1['token'], pub_c_id_1)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_2['u_id'] in member_u_ids)
    assert(user_3['u_id'] in member_u_ids)

def test_invite_others_private(register_users):
    '''
    Tests for invitation success: user 1 succesfully adds user 2 and 3 to 
    channel_1 (private).  
    '''

    (user_1, user_2, user_3) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', False)['channel_id']

    assert(channel.channel_invite(user_1['token'], priv_c_id_1, user_2['u_id']) == {})
    assert(channel.channel_invite(user_1['token'], priv_c_id_1, user_3['u_id']) == {})

    all_members = channel.channel_details(user_1['token'], priv_c_id_1)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_2['u_id'] in member_u_ids)
    assert(user_3['u_id'] in member_u_ids)

def test_invite_global_owner(register_users):
    '''
    Tests for global owner invitatation success: user 1 is a global owner and is
    invited to channel_2 (private) and channel_3 (private).
    '''

    (user_1, user_2, user_3) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', False)['channel_id']
    priv_c_id_3 = channels.channels_create(user_3['token'], 'Channelname', False)['channel_id']
    
    assert(channel.channel_invite(user_2['token'], priv_c_id_2, user_1['u_id']) == {})
    assert(channel.channel_invite(user_3['token'], priv_c_id_3, user_1['u_id']) == {})

    owner_members = channel.channel_details(user_2['token'], priv_c_id_2)['owner_members']
    owner_u_ids = [owner['u_id'] for owner in owner_members]
    assert(user_1['u_id'] in owner_u_ids)
    
    all_members = channel.channel_details(user_3['token'], priv_c_id_3)['all_members']
    member_u_ids = [member['u_id'] for member in all_members]
    assert(user_1['u_id'] in member_u_ids)
