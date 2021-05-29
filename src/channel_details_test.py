# -------------------------- Tests for channel_details -------------------------

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
    user_2 = auth.auth_register('user2@gmail.com', '123456', 'Givenname', 'Lastname')
    user_3 = auth.auth_register('user3@gmail.com', '123456', 'Name', 'Familyname')
    
    return (user_1, user_2, user_3)

def test_details_invalid_channel(register_users):
    '''
    Tests for invalid channels: user 1 tries to get details for non-existent channel.
    '''

    (user_1, _, _) = register_users

    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], 0)
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], -1)
    with pytest.raises(InputError):
        channel.channel_details(user_1['token'], 100)

def test_details_invalid_token(register_users):
    '''
    Tests for invalid token: invalid token.
    '''

    (user_1, _, _) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    token = user_1['token']

    with pytest.raises(AccessError):
        channel.channel_details(token + '1', pub_c_id_1)
    with pytest.raises(AccessError):
        channel.channel_details(token + ' ', pub_c_id_1)
    with pytest.raises(AccessError):
        channel.channel_details(' ', pub_c_id_1)

def test_details_non_member_public(register_users):
    '''
    Tests for non-member: user 1 tries to get details for channel_2 (public).
    '''

    (user_1, user_2, _) = register_users
    pub_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', True)['channel_id']
    
    with pytest.raises(AccessError):
        channel.channel_details(user_1['token'], pub_c_id_2)

def test_details_non_member_private(register_users):
    '''
    Tests for non-member: user 1 tries to get details for channel_2 (private).
    '''

    (user_1, user_2, _) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', False)['channel_id']

    with pytest.raises(AccessError):
        channel.channel_details(user_1['token'], priv_c_id_2)

def test_details_success_public(register_users):
    '''
    Tests for successful channel details: user 1 gets details for channel_1 (public).
    '''

    (user_1, _, _) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']

    assert channel.channel_details(user_1['token'], pub_c_id_1) == {
        'name': 'Channelname', 
        'owner_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }
        ], 
        'all_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }
        ],
    }

def test_details_success_private(register_users):
    '''
    Tests for successful channel details: user 2 gets details for channel_2 (private).
    '''

    (_, user_2, _) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'Channelname', False)['channel_id']
   
    assert channel.channel_details(user_2['token'], priv_c_id_2) == {
        'name': 'Channelname', 
        'owner_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            }
        ], 
        'all_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            }
        ],
    }

def test_details_success_many_owners(register_users):
    '''
    Tests for channel details success for multiple owners.
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    
    channel.channel_join(user_2['token'], pub_c_id_1)
    channel.channel_addowner(user_1['token'], pub_c_id_1, user_2['u_id'])
    channel.channel_join(user_3['token'], pub_c_id_1)
    channel.channel_addowner(user_1['token'], pub_c_id_1, user_3['u_id'])

    assert channel.channel_details(user_1['token'], pub_c_id_1) == {
        'name': 'Channelname', 
        'owner_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }, 
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_3['u_id'], 
                'name_first': 'Name', 
                'name_last': 'Familyname'
            },
        ], 
        'all_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            },
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_3['u_id'], 
                'name_first': 'Name', 
                'name_last': 'Familyname'
            },
        ],
    }

def test_details_success_many_members(register_users):
    '''
    Tests for channel details success for multiple members.
    '''

    (user_1, user_2, user_3) = register_users
    pub_c_id_1 = channels.channels_create(user_1['token'], 'Channelname', True)['channel_id']
    
    channel.channel_join(user_2['token'], pub_c_id_1)
    channel.channel_join(user_3['token'], pub_c_id_1)

    assert channel.channel_details(user_1['token'], pub_c_id_1) == {
        'name': 'Channelname', 
        'owner_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }, 
        ], 
        'all_members': [
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            },
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_3['u_id'], 
                'name_first': 'Name', 
                'name_last': 'Familyname'
            },
        ],
    }
