from error import AccessError, InputError
import user
import auth
import pytest
import other

@pytest.fixture
def user_login():
    '''
    log a user in and yield its associated session, clean everything afterwise
    '''

    auth.auth_register('name1@gmail.com', 'password1', 'name_first1', 'name_last1')
    session = auth.auth_register('name2@gmail.com', 'password2', 'name_first2', 'name_last2')
    yield session
    other.clear()

def test_user_AccessError(user_login):
    '''
    expected AccessError due to invalid token
    '''

    with pytest.raises(AccessError):
        user.user_profile("123", user_login['u_id'])
    with pytest.raises(AccessError):
        user.user_profile_setname("123", "name_first3", "name_last3")
    with pytest.raises(AccessError):
        user.user_profile_setemail("123", "name3@gmail.com")
    with pytest.raises(AccessError):
        user.user_profile_sethandle("123", "handle_str3")

def test_user_profile(user_login):
    '''
    successful request of user info
    '''

    assert(user.user_profile(user_login['token'], user_login['u_id']) == {"user": {'u_id': 2, 'email': "name2@gmail.com", 'name_first': "name_first2", 'name_last': "name_last2", 'handle_str': "name_first2name_last"}})

def test_user_profile_InputError(user_login):
    '''
    expected InputError due to invalid u_id
    '''

    with pytest.raises(InputError):
        user.user_profile(user_login['token'], 888)
    with pytest.raises(InputError):
        user.user_profile(user_login['token'], 999)
    
def test_user_setname(user_login):
    '''
    successful update of an user's name
    '''

    user.user_profile_setname(user_login['token'], "name_first3", "name_last3")
    assert(user.user_profile(user_login['token'], user_login['u_id']) == {"user": {'u_id': 2, 'email': "name2@gmail.com", 'name_first': "name_first3", 'name_last': "name_last3", 'handle_str': "name_first2name_last"}})

def test_user_setname_InputError(user_login):
    '''
    Expected InputError due to long name
    '''

    with pytest.raises(InputError):
        user.user_profile_setname(user_login['token'], "first_name_too_long_first_name_too_long_first_name_too_long", "name_last3")
    with pytest.raises(InputError):
        user.user_profile_setname(user_login['token'], "name_first3", "second_name_too_long_second_name_too_long_second_name_too_long")

def test_user_setemail(user_login):
    '''
    successful update of an user's email address
    '''

    user.user_profile_setemail(user_login['token'], "name3@gmail.com")
    assert(user.user_profile(user_login['token'], user_login['u_id']) == {"user": {'u_id': 2, 'email': "name3@gmail.com", 'name_first': "name_first2", 'name_last': "name_last2", 'handle_str': "name_first2name_last"}})

def test_user_setemail_InputError_invalidFormat(user_login):
    '''
    expected InputError due to invalid email format
    '''

    with pytest.raises(InputError):
        user.user_profile_setemail(user_login['token'], "invalidemail")
    with pytest.raises(InputError):
        user.user_profile_setemail(user_login['token'], "")

def test_user_setemail_InputError_emailDuplicate(user_login):
    '''
    exptected InputError due to duplicate email address
    '''

    with pytest.raises(InputError):
        user.user_profile_setemail(user_login['token'], "name1@gmail.com")
    
def test_user_sethandle(user_login):
    '''
    successful update of user's handle string
    '''

    user.user_profile_sethandle(user_login['token'], "handle_str3")
    assert(user.user_profile(user_login['token'], user_login['u_id']) ==  {"user": {'u_id': 2, 'email': "name2@gmail.com", 'name_first': "name_first2", 'name_last': "name_last2", 'handle_str': "handle_str3"}})

def test_user_sethanle_InputError_InvalidHandle(user_login):
    '''
    exptected InputError due to invalid handle string
    '''

    with pytest.raises(InputError):
        user.user_profile_sethandle(user_login['token'], "a")
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_login['token'], "idhoidhoidhdiodiihdhdis")

def test_user_sethanle_InputError_handleDuplicate(user_login):
    '''
    exptected InputError due to handle string already been used
    '''
    
    with pytest.raises(InputError):
        user.user_profile_sethandle(user_login['token'], "name_first1name_last")
