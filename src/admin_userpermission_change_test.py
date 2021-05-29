# -------------------- Tests for admin_userpermission_change -------------------

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

# Tests for invalid token.
def test_permission_change_invalid_token(register_users):
    (user_1, _, _) = register_users

    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_1['token'] + '1', user_1['u_id'], 1)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(' ', user_1['u_id'], 1)

# Tests for invalid users: user 1 to changes the permissions a non-existent user. 
def test_permission_change_invalid_user(register_users):
    (user_1, user_2, user_3) = register_users
    u_id_1 = user_1['u_id'] + user_2['u_id'] + user_3['u_id']
    u_id_2 = -user_1['u_id'] - user_2['u_id'] - user_3['u_id']

    with pytest.raises(InputError):
        other.admin_userpermission_change(user_1['token'], u_id_1, 1)
    with pytest.raises(InputError):
        other.admin_userpermission_change(user_1['token'], u_id_2, 2)

# Tests for invalid permission id.
def test_permission_change_invalid_permission_id(register_users):
    (user_1, user_2, user_3) = register_users

    with pytest.raises(InputError):
        other.admin_userpermission_change(user_1['token'], user_2['u_id'], 0)
    with pytest.raises(InputError):
        other.admin_userpermission_change(user_1['token'], user_3['u_id'], -1)
    with pytest.raises(InputError):
        other.admin_userpermission_change(user_1['token'], user_2['u_id'], 3)

# Tests for unauthorised user: user 2 and 3 are not global owners and change 
# each others' permissions.
def test_permission_change_members_reset_members(register_users):
    (_, user_2, user_3) = register_users

    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_2['token'], user_3['u_id'], 1)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_2['token'], user_3['u_id'], 2)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_3['token'], user_2['u_id'], 1)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_3['token'], user_2['u_id'], 2)

# Tests for unauthorised user: user 2 and 3 are not global owners and change the 
# global owner's permission. 
def test_permission_change_members_reset_global_owner(register_users):
    (user_1, user_2, user_3) = register_users

    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_2['token'], user_1['u_id'], 1)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_2['token'], user_1['u_id'], 2)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_3['token'], user_1['u_id'], 1)
    with pytest.raises(AccessError):
        other.admin_userpermission_change(user_3['token'], user_1['u_id'], 2)

# Tests for global owner promoting another member.
def test_permission_change_global_owner_reset_members(register_users):
    (user_1, user_2, _) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'channel1', False)['channel_id']

    other.admin_userpermission_change(user_1['token'], user_2['u_id'], 1)
    
    channel.channel_join(user_2['token'], priv_c_id_1)
    assert channel.channel_details(user_2['token'], priv_c_id_1) == {

        'name': 'channel1', 
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
        ],
    }

# Tests for global owner demoting another global owner. 
def test_permission_change_global_owner_reset_owner(register_users):
    (user_1, user_2, _) = register_users
    priv_c_id_1 = channels.channels_create(user_1['token'], 'channel1', False)['channel_id']

    other.admin_userpermission_change(user_1['token'], user_2['u_id'], 1)
    other.admin_userpermission_change(user_1['token'], user_2['u_id'], 2)

    with pytest.raises(AccessError):
        channel.channel_join(user_2['token'], priv_c_id_1)

# Tests for global owner promoting themselves (no effect).
def test_permission_change_global_owner_promote_self(register_users):
    (user_1, user_2, _) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'channel2', False)['channel_id']

    other.admin_userpermission_change(user_1['token'], user_1['u_id'], 1)
    channel.channel_join(user_1['token'], priv_c_id_2)
    assert channel.channel_details(user_1['token'], priv_c_id_2) == {

        'name': 'channel2', 
        'owner_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }, 
        ], 
        'all_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            },
        ],
    }

# Tests for global owner demoting themselves (no effect).
def test_permission_change_global_owner_demote_self(register_users):
    (user_1, user_2, _) = register_users
    priv_c_id_2 = channels.channels_create(user_2['token'], 'channel2', False)['channel_id']

    other.admin_userpermission_change(user_1['token'], user_1['u_id'], 2)

    channel.channel_join(user_1['token'], priv_c_id_2)
    assert channel.channel_details(user_1['token'], priv_c_id_2) == {

        'name': 'channel2', 
        'owner_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            }, 
        ], 
        'all_members': [
            {
                'u_id': user_2['u_id'], 
                'name_first': 'Givenname', 
                'name_last': 'Lastname'
            },
            {
                'u_id': user_1['u_id'], 
                'name_first': 'Firstname', 
                'name_last': 'Surname'
            },
        ],
    }
