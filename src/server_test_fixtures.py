# Fixtures for server tests

import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

@pytest.fixture(scope="session")
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGTERM)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

@pytest.fixture
def register_users(url):
    # register user 1 (global owner)
    register = requests.post(f"{url}/auth/register", json={
        'email': 'user1@gmail.com',
        'password': 'password1',
        'name_first': 'name_1',
        'name_last': 'surname_1',
    })

    user_1 = register.json()

    # register user 2
    register = requests.post(f"{url}/auth/register", json={
        'email': 'user2@gmail.com',
        'password': 'password2',
        'name_first': 'name_2',
        'name_last': 'surname_2',
    })

    user_2 = register.json()

    # register user 3
    register = requests.post(f"{url}/auth/register", json={
        'email': 'user3@gmail.com',
        'password': 'password3',
        'name_first': 'name_3',
        'name_last': 'surname_3',
    })

    user_3 = register.json()

    yield (user_1, user_2, user_3)
    
    requests.delete(f"{url}/clear")


@pytest.fixture
def create_channels(url, register_users):
    (user_1, user_2, _) = register_users
    
    channel = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'pub_c_1',
        'is_public': True
    })

    payload = channel.json()
    pub_c_id_1 = payload['channel_id']

    channel = requests.post(f"{url}/channels/create", json={
        'token': user_1['token'],
        'name': 'priv_c_1',
        'is_public': False
    })

    payload = channel.json()
    priv_c_id_1 = payload['channel_id']

    channel = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'pub_c_2',
        'is_public': True
    })

    payload = channel.json()
    pub_c_id_2 = payload['channel_id']

    channel = requests.post(f"{url}/channels/create", json={
        'token': user_2['token'],
        'name': 'priv_c_2',
        'is_public': False
    })

    payload = channel.json()
    priv_c_id_2 = payload['channel_id']

    return (pub_c_id_1, priv_c_id_1, pub_c_id_2, priv_c_id_2)
