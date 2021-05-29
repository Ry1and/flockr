# ---------------------------- Tests for users_all -----------------------------

import pytest
from error import InputError, AccessError
import auth
import channel
import other 
import user

@pytest.fixture    
def register_users():
    other.clear()
    # user 1 is a global owner (1st person to sign up)
    user_1 = auth.auth_register('user1@gmail.com', '123456', 'Givenname', 'Lastname')
    user_2 = auth.auth_register('user2@gmail.com', '123456', 'Firstname', 'Surname')
    user_3 = auth.auth_register('user3@gmail.com', '123456', 'Name', 'Familyname')

    return (user_1, user_2, user_3)

# Tests for invalid token.
def test_users_all_invalid_token(register_users):
    (user_1, _, _) = register_users
    token = user_1['token']

    with pytest.raises(AccessError):
        other.users_all(token + '1')
    with pytest.raises(AccessError):
        other.users_all(' ')
    with pytest.raises(AccessError):
        other.users_all(token + ' ')

# Tests for users_all return success for global owner.
def test_users_all_success_global_owner(register_users):
    (user_1, user_2, user_3) = register_users
    handle_1 = 'handle_1'
    handle_2 = 'handle_2'
    handle_3 = 'handle_3'

    user.user_profile_sethandle(user_1['token'], handle_1)
    user.user_profile_sethandle(user_2['token'], handle_2)
    user.user_profile_sethandle(user_3['token'], handle_3)

    assert other.users_all(user_1['token']) == {
        'users': [
            {
                'u_id': user_1['u_id'],
                'email': 'user1@gmail.com',
                'name_first': 'Givenname',
                'name_last': 'Lastname',
                'handle_str': handle_1,
            },
            {
                'u_id': user_2['u_id'],
                'email': 'user2@gmail.com',
                'name_first': 'Firstname',
                'name_last': 'Surname',
                'handle_str': handle_2,
            },
            {
                'u_id': user_3['u_id'],
                'email': 'user3@gmail.com',
                'name_first': 'Name',
                'name_last': 'Familyname',
                'handle_str': handle_3,
            },
        ]
    }

# Tests for users_all return success for normal member.
def test_users_all_success_member(register_users):
    (user_1, user_2, user_3) = register_users
    handle_1 = 'handle_1'
    handle_2 = 'handle_2'
    handle_3 = 'handle_3'

    user.user_profile_sethandle(user_1['token'], handle_1)
    user.user_profile_sethandle(user_2['token'], handle_2)
    user.user_profile_sethandle(user_3['token'], handle_3)

    assert other.users_all(user_2['token']) == {
        'users': [
            {
                'u_id': user_1['u_id'],
                'email': 'user1@gmail.com',
                'name_first': 'Givenname',
                'name_last': 'Lastname',
                'handle_str': handle_1,
            },
            {
                'u_id': user_2['u_id'],
                'email': 'user2@gmail.com',
                'name_first': 'Firstname',
                'name_last': 'Surname',
                'handle_str': handle_2,
            },
            {
                'u_id': user_3['u_id'],
                'email': 'user3@gmail.com',
                'name_first': 'Name',
                'name_last': 'Familyname',
                'handle_str': handle_3,
            },
        ]
    }
