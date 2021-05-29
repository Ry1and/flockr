import random
import data
import hashlib
import re
from data import account_search
from error import AccessError, InputError
import jwt
from flask import request


regex_email = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def auth_login(email, password):
    '''
    Logs in a user given a registered email and valid password.

    Args:
        email (str): email of the user who is attempting to log in.
        password (str): password corresponding to the email of the user who is logging in. 

    Return:
        { u_id, token }

    Raises:
        InputError: The email entered is not a valid email, the email entered does not
        belong to a user, or the password is incorrect. 
    '''

    # email checking
    # invalid email format
    if not re.search(regex_email, email):
        raise InputError(description='Invalid email address')
    
    # search account
    account = data.account_search("email", email)

    # email is not found to belong to any account
    if not account:
        raise InputError(description='Email address not found')
    
    # password checking
    password = hashlib.sha256(password.encode()).hexdigest()

    if account['password'] != password:
        raise InputError(description='Incorrect password')

    # generate token and create session
    token = token_generate(account['u_id'], account['handle_str'])

    # check if this user already has an active session, if there is, delete it
    session = data.session_search("u_id", account['u_id'])
    if session:
        data.delete_session(session)
    
    # link token with u_id (create a new session for this registration)
    new_session = {
        'token': token,
        'u_id': account['u_id']
    }

    data.sessions.append(new_session)

    # everything good, return an active token and user's id
    return new_session

def auth_logout(token):
    '''
    Given an active token, invalidates the token to log the user out. If a valid 
    token is given, and the user is successfully logged out, it returns true, 
    otherwise false.

    Args:
        token (str): Token of the user who is logging out.

    Return:
        { is_success }

    Raises:
        AccessError: The token does not exist.
    '''

    logout_session = data.session_search("token", token)
    # if token exist and is active, delete the whole session
    if logout_session:
        data.sessions.remove(logout_session)
        if not data.session_search("token", token):
            return {'is_success': True}
    else:
        raise AccessError('Session does not exist')
        
def auth_register(email, password, name_first, name_last):
    '''
    Register and create an account for user given a valid email, password, name_first
    and name_last.

    Args:
       email (str): email of the user attempting to register.
       password (str): password of the user attempting to register.
       name_first (str): first name of the user attempting to register.
       name_last (str): last name of the user attempting to register.

    Return:
        { u_id, token }

    Raises:
        InputError: The email is not a valid, the email has been used by another user, 
        password entered is less than 6 characters long, or name_first or name_last is 
        not between 1 and 50 characters (inclusive).
    '''

    # email checking
    # invalid email format
    if not re.search(regex_email, email):
        raise InputError(description='Invalid email address')

    # email address being used
    account = data.account_search("email", email)
    if account:
        raise InputError(description='Email address has been used')
    
    # password checking
    # password is less than 6 characters long
    if len(password) < 6:
        raise InputError(description='Password must be longer than 6 characters') 
    
    # name checking
    # first name is not between 1 and 50 characters long
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description='Name must be between 1 and 50')
    
    # last name is not between 1 and 50 characters long
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description='Name must be between 1 and 50')

    # generate handle
    handle = (name_first.lower() + name_last.lower())[:20]

    # if handle is used, reverse the handle
    if account_search("handle_str", handle):
        handle = ''.join(random.sample(handle, len(handle)))

    # hash the password
    password = hashlib.sha256(password.encode()).hexdigest()

    # create account and store info
    new_account = {
        'u_id': 0,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'password': password,
        'handle_str': handle
    }

    u_id = data.new_account(new_account)

    # generate unique token
    token = token_generate(u_id, handle)

    # link token with u_id (create a session for this registration)
    session = {
        'token': token,
        'u_id': u_id
    }

    data.new_session(session)

    # return an active token and u_id
    return session

# generate a unique token
def token_generate(u_id, secret):
    '''
    Generate a token given a u_id and secret. 

    Args:
        u_id (int): u_id of the user the token is being generated for. 
        secret (str): secret to encode the token with. 

    Return:
        token

    Raises:
        NA
    '''

    # encode u_id with handle_str and decode it into utf-8 form
    token = jwt.encode({'u_id': u_id}, secret, algorithm='HS256').decode("utf-8")
    return token
    
def auth_setpassword(reset_code, new_password): # pragma: no cover
    '''
    Given a unique reset_code and new password, change the user's password.

    Args: 
        reset_code (str): reset_code for resetting a new password.
        new_password (str): new password to be resetted.

    Return:
        {} 
    
    Raises:
        InputError: The reset_code is an invalid reset code, or the password entered 
        is invalid. 
    '''

    reset_user = data.reset_list_search("reset_code", reset_code)
    if not reset_user:
        raise InputError(description='invalid reset_code')
    if len(new_password) < 6:
        raise InputError(description='Password must be longer than 6 characters') 
    u_id = data.account_search("email", reset_user['email'])["u_id"]
    password = hashlib.sha256(new_password.encode()).hexdigest()
    data.update_account(u_id, "password", password)
    data.reset_list_remove(reset_code)
    return {}
