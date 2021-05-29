from subprocess import Popen, PIPE
from flask.globals import request
from requests.models import Response
from error import AccessError, InputError
from auth_server_test_data import DATA_COLLECTION
from server_test_fixtures import url, register_users, create_channels
from other import clear
from time import sleep
import pytest
import re
import signal
import requests
from auth import auth_setpassword

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    
    assert url.startswith("http")

def test_auth_passwordreset_request(url):
    '''
    successful request of changing password
    '''

    for i in DATA_COLLECTION["auth_register"]:
        assert requests.post(f"{url}/auth/register", json = i)
    for i in DATA_COLLECTION["auth_register"]:
        assert requests.post(f"{url}/auth/passwordreset/request", json = {"email": i["email"]})
    requests.delete(f"{url}/clear")

def test_auth_passwordreset_reset(url):
    '''
    successful request of changing password
    '''

    reset_code = []
    for i in DATA_COLLECTION["auth_register"]:
        assert requests.post(f"{url}/auth/register", json = i)
    for i in DATA_COLLECTION["auth_register"]:
        code = requests.post(f"{url}/auth/passwordreset/request", json = {"email": i["email"]}).json()["reset_code"]
        reset_code.append(code)
    for i in range(0, len(DATA_COLLECTION["auth_register"])):
        assert requests.post(f"{url}/auth/passwordreset/reset", json = {"reset_code": reset_code[i], "new_password": "new"+DATA_COLLECTION["auth_register"][i]["password"]})
    requests.delete(f"{url}/clear")

def test_auth_passwordreset_InputError(url):
    '''
    unsuccessful request of changing password due to invalid reset code or password
    '''

    assert requests.post(f"{url}/auth/register", json = DATA_COLLECTION["auth_register"][0])
    code = requests.post(f"{url}/auth/passwordreset/request", json = {"email": DATA_COLLECTION["auth_register"][0]["email"]}).json()["reset_code"]
    # invalid reset code
    r = requests.post(f"{url}/auth/passwordreset/reset", json = {"reset_code": 1234567, "new_password": "newpassword1"})
    assert r.status_code == InputError.code
    # invalid password
    r = requests.post(f"{url}/auth/passwordreset/reset", json = {"reset_code": code, "new_password": "123"})
    assert r.status_code == InputError.code
    requests.delete(f"{url}/clear")
