# ---------------------- Tests for user_profile_uploadphoto --------------------

import pytest
from error import InputError, AccessError
import auth
import channel
import channels
import other
import user

@pytest.fixture
def register_users():
    other.clear()
    # user 1 is a global owner (1st person to sign up)
    user_1 = auth.auth_register('user1@gmail.com', '123456', 'Firstname', 'Surname')
    user_2 = auth.auth_register('user2@gmail.com', '123456', 'Givenname', 'Lastname')
    user_3 = auth.auth_register('user3@gmail.com', '123456', 'Name', 'Familyname')
    
    return (user_1, user_2, user_3)

def test_uploadphoto_invalid_token(register_users):
    '''
    Tests for error raised when an invalid token is given.
    '''

    invalid_token = 'invalidtoken'
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    with pytest.raises(AccessError):
        user.user_profile_uploadphoto(invalid_token, img_url, 0, 0, 100, 100)

def test_uploadphoto_invalid_url(register_users):
    '''
    Tests for error raised when the an invalid img_url is given.
    '''
    
    (user_1, _, _) = register_users
    invalid_img_url = 'invalidurl'

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], invalid_img_url, 0, 0, 100, 100)

def test_uploadphoto_unretrievable_url(register_users):
    '''
    Tests for error raised when the an img_url that cannot be retrieved is given.
    '''

    (user_1, _, _) = register_users
    unretrievable_url = 'https://cdn.pixabay.com/photo/2017/08/30/01/05/milky-way-2695569__340.jpg'

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], unretrievable_url, 0, 0, 100, 100)

def test_uploadphoto_http_status(register_users):
    '''
    Tests for error raised when a HTTP status other than 200 is returned.
    '''

    (user_1, _, _) = register_users
    invalid_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jp'

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], invalid_url, 0, 0, 100, 100)

def test_uploadphoto_crop_beyond_dimensions(register_users):
    '''
    Tests for error raised when x_start, y_start, x_end, y_end are beyond image 
    dimensions.
    '''

    (user_1, user_2, user_3) = register_users
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'
    # (dimensions: 640 x 480)

    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 0, 0)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_2['token'], img_url, 0, 0, 641, 100)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_3['token'], img_url, 0, 0, 100, 481)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 100, 0, 50, 100)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_2['token'], img_url, 50, 100, 100, 50)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_3['token'], img_url, 641, 0, 642, 480)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, 481, 640, 482)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, -10, 10, -1, 100)
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], img_url, 0, -1, 0, 100)

def test_uploadphoto_not_jpg(register_users):
    '''
    Tests for error raised when an invalid image format is given.
    '''
    
    (user_1, _, _) = register_users
    png_url = 'https://wallpapercave.com/wp/wp2832050.png'
    
    with pytest.raises(InputError):
        user.user_profile_uploadphoto(user_1['token'], png_url, 0, 0, 100, 100)

def test_uploadphoto_success(register_users):
    '''
    Tests for no error raised when a valid token, img_url and dimensions are 
    given.
    '''

    (user_1, _, _) = register_users
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    assert user.user_profile_uploadphoto(user_1['token'], img_url, 0, 0, 100, 100) == {}
