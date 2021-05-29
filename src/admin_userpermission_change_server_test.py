# ----------------- Tests for admin/userpermission/change route ----------------

# pytest.fixture and test_url copied from the provided file echo_http_test.py

import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from error import AccessError, InputError
from server_test_fixtures import url, register_users

def test_url(url):
    '''
    A simple sanity test to check that the server is set up properly
    '''
    assert url.startswith("http")

# Tests for error when given an invalid token.
def test_permission_change_invalid_token(url, register_users):
    (_, user_2, _) = register_users

    invalid_token = 'invalid_token'

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': invalid_token, 'u_id': user_2['u_id'], 'permission_id': 1})

    assert permission.status_code == AccessError.code

# Tests for error when given an invalid user_id.
def test_permission_change_invalid_user(url, register_users):
    (user_1, user_2, _) = register_users

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_1['token'], 'u_id': user_1['u_id'] + user_2['u_id'] + 1,
    'permission_id': 1})

    assert permission.status_code == InputError.code

# Tests for error when given an invalid permission_id.
def test_permission_change_invalid_permission_id(url, register_users):
    (user_1, user_2, _) = register_users

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_1['token'], 'u_id': user_2['u_id'], 'permission_id': 0})

    assert permission.status_code == InputError.code

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_1['token'], 'u_id': user_2['u_id'], 'permission_id': 3})

    assert permission.status_code == InputError.code

# Tests for error when member tries to change another user's permission.
def test_permission_change_member_others(url, register_users):
    (user_1, user_2, user_3) = register_users

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_2['token'], 'u_id': user_1['u_id'], 'permission_id': 2})

    assert permission.status_code == AccessError.code

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_3['token'], 'u_id': user_2['u_id'], 'permission_id': 1})

    assert permission.status_code == AccessError.code

# Tests for error when a member tries to change their own permission.
def test_permission_change_member_self(url, register_users):
    (_, user_2, _) = register_users

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_2['token'], 'u_id': user_2['u_id'], 'permission_id': 2})

    assert permission.status_code == AccessError.code

# Tests for success when an owner changes another member's permission.
def test_permission_change_owner_owner(url, register_users):
    (user_1, user_2, _) = register_users

    permission = requests.post(f"{url}/admin/userpermission/change", json={
        'token': user_1['token'], 
        'u_id': user_2['u_id'], 
        'permission_id': 1
    })

    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_2['token'], 'u_id': user_1['u_id'], 'permission_id': 2})
    
    permission = requests.post(f"{url}/admin/userpermission/change", json={
    'token': user_1['token'], 'u_id': user_2['u_id'], 'permission_id': 1})

    assert permission.status_code == AccessError.code
