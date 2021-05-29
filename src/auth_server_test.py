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

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    
    assert url.startswith("http")

def test_auth_register(url):
    '''
    successful request of user register
    '''

    for i in DATA_COLLECTION["auth_register"]:
        assert requests.post(f"{url}/auth/register", json = i)
    requests.delete(f"{url}/clear")

def test_auth_register_fail(url):
    '''
    bad request due to register InputError
    '''

    requests.post(f"{url}/auth/register", json = DATA_COLLECTION["auth_register"][0])
    for i in DATA_COLLECTION["auth_register_fail"]:
        r = requests.post(f"{url}/auth/register", json = i)
        assert r.status_code == InputError.code
    requests.delete(f"{url}/clear")

def test_auth_login(url):
    '''
    successful request of user login
    '''

    for i in DATA_COLLECTION["auth_register"]:
        assert requests.post(f"{url}/auth/register", json = i)
    for i in DATA_COLLECTION["auth_login"]:
        assert requests.post(f"{url}/auth/login", json = i)
    requests.delete(f"{url}/clear")

def test_auth_login_fail(url):
    '''
    bad request due to login InputError
    '''

    requests.post(f"{url}/auth/register", json = DATA_COLLECTION["auth_register"][0])
    for i in DATA_COLLECTION["auth_login_fail"]:
        r = requests.post(f"{url}/auth/login", json = i)
        assert r.status_code == InputError.code
    requests.delete(f"{url}/clear")

def test_auth_logout(url):
    '''
    successful request of user logout
    '''

    for i in DATA_COLLECTION["auth_register"]:
        token = requests.post(f"{url}/auth/register", json = i).json()["token"]
        assert requests.post(f"{url}/auth/logout", json = {"token": token})
    requests.delete(f"{url}/clear")

def test_auth_logout_fail(url):
    '''
    bad request due to logout AccessError
    '''

    requests.post(f"{url}/auth/register", json = DATA_COLLECTION["auth_register"][0])
    r = requests.post(f"{url}/auth/logout", json = {"token": "wetrewxxsq"})
    assert r.status_code == AccessError.code
    requests.delete(f"{url}/clear")
