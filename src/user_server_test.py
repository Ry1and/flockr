from server_test_fixtures import url, register_users
from subprocess import Popen, PIPE
from flask.globals import request
from requests.models import Response
from error import AccessError, InputError
from time import sleep
import re
import pytest
import signal
import requests

INVALID_TOKEN = "invalidtoken"
INVALID_U_ID = 0

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    assert url.startswith("http")

def test_AccessError(url, register_users):
    '''
    unsuccessful requests due to invalid token
    '''

    (_, _, user_3) = register_users
    r = requests.get(f"{url}/user/profile?token={INVALID_TOKEN}&u_id={user_3['u_id']}")
    assert r.status_code == AccessError.code
    r = requests.put(f"{url}/user/profile/setname", json={"token": INVALID_TOKEN, "name_first": "name_4", "name_last": "surname_4"})
    assert r.status_code == AccessError.code
    r = requests.put(f"{url}/user/profile/setemail", json={"token": INVALID_TOKEN, "email": "user4@gmail.com"})
    assert r.status_code == AccessError.code
    r = requests.put(f"{url}/user/profile/sethandle", json={"token": INVALID_TOKEN, "handle_str": "handle_str4"})
    assert r.status_code == AccessError.code

def test_user_profile(url, register_users):
    '''
    successful request of user profile
    '''

    (_, _, user_3) = register_users
    r = requests.get(f"{url}/user/profile?token={user_3['token']}&u_id={user_3['u_id']}")

    payload = r.json()

    assert len(payload) == 1
    assert len(payload["user"]) == 6
    assert payload["user"]['u_id'] == 3
    assert payload["user"]['email'] == 'user3@gmail.com'
    assert payload["user"]['name_first'] == 'name_3'
    assert payload["user"]['name_last'] == 'surname_3'
    assert payload["user"]['handle_str'] == 'name_3surname_3'
    assert payload["user"]['profile_img_url'].startswith(url)

def test_user_profile_InputError(url, register_users):
    '''
    unsuccessful request of user profile due to InputError
    '''

    (_, _, user_3) = register_users
    r = requests.get(f"{url}/user/profile?token={user_3['token']}&u_id={INVALID_U_ID}")
    assert r.status_code == InputError.code

def test_user_setname(url, register_users):
    '''
    successful request of user setname
    '''

    (_, _, user_3) = register_users
    requests.put(f"{url}/user/profile/setname", json={"token": user_3['token'], "name_first": "name_4", "name_last": "surname_4"})
    r = requests.get(f"{url}/user/profile?token={user_3['token']}&u_id={user_3['u_id']}")

    payload = r.json()

    assert len(payload) == 1
    assert len(payload["user"]) == 6
    assert payload["user"]['u_id'] == 3
    assert payload["user"]['email'] == 'user3@gmail.com'
    assert payload["user"]['name_first'] == 'name_4'
    assert payload["user"]['name_last'] == 'surname_4'
    assert payload["user"]['handle_str'] == 'name_3surname_3'
    assert payload["user"]['profile_img_url'].startswith(url)

def test_user_setname_InputError(url, register_users):
    '''
    unsuccessful request of user setname due to invalid name
    '''

    (_, _, user_3) = register_users
    r = requests.put(f"{url}/user/profile/setname", json={"token": user_3['token'], "name_first": "first_name_too_long_first_name_too_long_first_name_too_long", "name_last": "surname_4"})
    assert r.status_code == InputError.code
    r = requests.put(f"{url}/user/profile/setname", json={"token": user_3['token'], "name_first": "name_4", "name_last": "last_name_too_long_last_name_too_long_last_name_too_long"})
    assert r.status_code == InputError.code

def test_user_setemail(url, register_users):
    '''
    successful request of user setemail
    '''

    (_, _, user_3) = register_users
    requests.put(f"{url}/user/profile/setemail", json={"token": user_3['token'], "email": "user4@gmail.com"})
    r = requests.get(f"{url}/user/profile?token={user_3['token']}&u_id={user_3['u_id']}")

    payload = r.json()

    assert len(payload) == 1
    assert len(payload["user"]) == 6
    assert payload["user"]['u_id'] == 3
    assert payload["user"]['email'] == 'user4@gmail.com'
    assert payload["user"]['name_first'] == 'name_3'
    assert payload["user"]['name_last'] == 'surname_3'
    assert payload["user"]['handle_str'] == 'name_3surname_3'
    assert payload["user"]['profile_img_url'].startswith(url)

def test_user_setemail_InputError_invalidFormat(url, register_users):
    '''
    unsuccessful request of user setemail due to invalid email format
    '''

    (_, _, user_3) = register_users
    r = requests.put(f"{url}/user/profile/setemail", json={"token": user_3['token'], "email": "invalidemail"})
    assert r.status_code == InputError.code

def test_user_setemail_InputError_emailDuplicate(url, register_users):
    '''
    unsuccessful request of user setemail due to duplicate email
    '''

    (_, _, user_3) = register_users
    r = requests.put(f"{url}/user/profile/setemail", json={"token": user_3['token'], "email": "user2@gmail.com"})
    assert r.status_code == InputError.code

def test_user_sethandle(url, register_users):
    '''
    successful request to user sethandle
    '''

    (_, _, user_3) = register_users
    requests.put(f"{url}/user/profile/sethandle", json={"token": user_3['token'], "handle_str": "handle_str4"})
    r = requests.get(f"{url}/user/profile?token={user_3['token']}&u_id={user_3['u_id']}")

    payload = r.json()

    assert len(payload) == 1
    assert len(payload["user"]) == 6
    assert payload["user"]['u_id'] == 3
    assert payload["user"]['email'] == 'user3@gmail.com'
    assert payload["user"]['name_first'] == 'name_3'
    assert payload["user"]['name_last'] == 'surname_3'
    assert payload["user"]['handle_str'] == 'handle_str4'
    assert payload["user"]['profile_img_url'].startswith(url)

def test_user_sethandle_InputError_invalidFormat(url, register_users):
    '''
    unsuccessful request of user sethandle due to invalid handle format
    '''

    (_, _, user_3) = register_users
    r = requests.put(f"{url}/user/profile/sethandle", json={"token": user_3['token'], "handle_str": "a"})
    assert r.status_code == InputError.code
    r = requests.put(f"{url}/user/profile/sethandle", json={"token": user_3['token'], "handle_str": "handle_string_too_long"})
    assert r.status_code == InputError.code

def test_user_sethandle_InputError_handleDuplicate(url, register_users):
    '''
    unsuccessful request of user sethandle due to duplicate handle
    '''

    (_, _, user_3) = register_users
    r = requests.put(f"{url}/user/profile/sethandle", json={"token": user_3['token'], "handle_str": "name_2surname_2"})
    assert r.status_code == InputError.code
