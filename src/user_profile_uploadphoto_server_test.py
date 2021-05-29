# ------------------- Tests for user/profile/uploadphoto route ------------------

import pytest
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users, create_channels

def test_uploadphoto_invalid_token(url, register_users):
    '''
    Tests for error raised when an invalid token is given. 
    '''

    invalid_token = 'invalidtoken'
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': invalid_token, 'img_url': img_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == AccessError.code

def test_uploadphoto_invalid_url(url, register_users):
    '''
    Tests for error raised when the an invalid img_url is given.
    '''

    (user_1, _, _) = register_users
    invalid_img_url = 'invalidurl'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': invalid_img_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == InputError.code

def test_uploadphoto_unretrievable_url(url, register_users):
    '''
    Tests for error raised when the an img_url that cannot be retrieved is given.
    '''

    (user_1, _, _) = register_users
    unretrievable_url = 'https://cdn.pixabay.com/photo/2017/08/30/01/05/milky-way-2695569__340.jpg'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': unretrievable_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == InputError.code

def test_uploadphoto_http_status(url, register_users):
    '''
    Tests for error raised when the http status returned is not 200.
    '''

    (user_1, _, _) = register_users
    invalid_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jp'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': invalid_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == InputError.code

def test_uploadphoto_crop_beyond_dimensions(url, register_users):
    '''
    Tests for error raised when the image is cropped beyond bounds x_start, 
    y_start, x_end, y_end.
    '''

    (user_1, user_2, user_3) = register_users
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': img_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 0, 'y_end': 0})
    
    assert photo.status_code == InputError.code

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_2['token'], 'img_url': img_url, 'x_start': 500, 'y_start': 0, 
    'x_end': 1000, 'y_end': 500})
    
    assert photo.status_code == InputError.code

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_3['token'], 'img_url': img_url, 'x_start': -1, 'y_start': 10, 
    'x_end': 1, 'y_end': 20})
    
    assert photo.status_code == InputError.code

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_3['token'], 'img_url': img_url, 'x_start': 0, 'y_start': -10, 
    'x_end': 10, 'y_end': -1})
    
    assert photo.status_code == InputError.code

def test_uploadphoto_not_jpg(url, register_users):
    '''
    Tests for error raised when the given image is not a JPG.
    '''

    (user_1, _, _) = register_users
    png_url = 'https://wallpapercave.com/wp/wp2832050.png'
    
    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': png_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == InputError.code

def test_uploadphoto_profile_success(url, register_users):
    '''
    Tests for no error raised when a valid token, img_url and dimensions are 
    given.
    '''

    (user_1, _, _) = register_users
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    photo = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': img_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert photo.status_code == 200
    assert photo.json() == {}

def test_uploadphoto_default_profile_channel_match(url, register_users, create_channels):
    '''
    Tests for user profile's default profile_img_url match with channel member's 
    default profile_img_url. 
    '''

    (user_1, _, _) = register_users
    t_1 = user_1['token']

    (pub_c_id_1, _, _, _) = create_channels

    users = requests.get(f"{url}/users/all?token={user_1['token']}")
    payload_1 = users.json()

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={pub_c_id_1}")
    payload_2 = details.json()

    assert payload_1['users'][0]['profile_img_url'] == payload_2['all_members'][0]['profile_img_url']
    assert payload_1['users'][0]['profile_img_url'] == payload_2['owner_members'][0]['profile_img_url']

def test_uploadphoto_change_profile_channel_match(url, register_users, create_channels):
    '''
    Tests for user profile's profile_img_url match with channel member's 
    profile_img_url after the default image has been changed. 
    '''

    (user_1, _, _) = register_users
    t_1 = user_1['token']

    (pub_c_id_1, _, _, _) = create_channels

    img_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/A_black_background.jpg/640px-A_black_background.jpg'

    r = requests.post(f"{url}/user/profile/uploadphoto", json={
    'token': user_1['token'], 'img_url': img_url, 'x_start': 0, 'y_start': 0, 
    'x_end': 100, 'y_end': 100})

    assert r.status_code == 200
    assert r.json() == {}

    users = requests.get(f"{url}/users/all?token={user_1['token']}")
    payload_1 = users.json()

    details = requests.get(f"{url}/channel/details?token={t_1}&channel_id={pub_c_id_1}")
    payload_2 = details.json()

    assert payload_1['users'][0]['profile_img_url'] == payload_2['all_members'][0]['profile_img_url']
    assert payload_1['users'][0]['profile_img_url'] == payload_2['owner_members'][0]['profile_img_url']
