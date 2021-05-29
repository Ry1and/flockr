from os import name
from error import AccessError, InputError
import hashlib
import data
import re
import urllib
import requests
from PIL import Image
import uuid
from flask import request

regex_email = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

def user_profile(token, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, 
    last name, and handle.

    Args:
        token (str): token of the user whose profile is being retrieved.
        u_id (int): u_id of the user whose profile is being retrieved.

    Return:
        { user }

    Raises:
        AccessError: The token is invalid. 
        InputError: The user with u_id is not a valid user.
    '''

    if not data.session_search("token", token):
        raise AccessError(description='Invalid token')
    account = data.account_search("u_id", u_id)
    if account:
        return {"user": data.make_user(account['u_id'])}
    else:
        raise InputError(description='User not exist')

def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first and last name.

    Args:
        token (str): token of the user who is attempting to change their name.
        name_first (str): new name_first the user wants to change their first 
        name to.
        name_last (str): new name_last the user wants to change their last 
        name to.

    Return:
        {}

    Raises:
        AccessError: The token is invalid.
        InputErrror: The given name_first or name_last is not between 1 and 50
        characters, inclusive.
    '''

    session = data.session_search("token", token)
    if not session:
        raise AccessError(description='Invalid token')

    # name checking
    # first name is not between 1 and 50 characters long
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description='Name must be between 1 and 50')
    
    # last name is not between 1 and 50 characters long
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description='Name must be between 1 and 50')
    data.update_account(session['u_id'], 'name_first', name_first)
    data.update_account(session['u_id'], 'name_last', name_last)
    return {}

def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address.

    Args:
        token (str): token of the user who is attempting to change their email.
        email (str): new email the user wants to change their email to.

    Return:
        {}

    Raises:
        AccessError: The token is invalid.  
        InputError: The given email is not a valid email or the email address is
        already being used by another user. 
    '''

    session = data.session_search("token", token)
    if not session:
        raise AccessError(description='Invalid token')

    # invalid email format
    if not re.search(regex_email, email):
        raise InputError(description='Invalid email address')

    # email address being used
    account = data.account_search("email", email)
    if account and account["u_id"] != session["u_id"]:
        raise InputError(description='Email address has been used')
    data.update_account(session['u_id'], 'email', email)
    return {}

def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name).

    Args:
        token (str): token of the user who is attempting to change their handle. 
        handle_str (str): the new handle_str the user wants to change their 
        handle to.

    Return:
        {}

    Raises:
        AccessError: The token is invalid.
        InputError: The given handle_str is not between 3 and 20 characters or 
        the handle is already being used by another user. 
    '''
    
    session = data.session_search("token", token)
    if not session:
        raise AccessError(description='Invalid token')

    # handle string is not within 3 to 20
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description='handle_str must be between 3 and 20')
    account = data.account_search("handle_str", handle_str)
    if account and account["u_id"] != session["u_id"]:
        raise InputError(description='handle_str has been used')
    data.update_account(session['u_id'], 'handle_str', handle_str)
    return {}

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end).

    Args:
        token (str): token of the user who is attempting to upload a new profile
        photo. 
        img_url (str): the url of the image the user is attempting to upload.
        x_start (int): the start x-coordinate to crop the image from. 
        y_start (int): the start y-coordinate to crop the image from.
        x_end (int): the end x-coordinate to crop the image to.
        y_end (int): the end y-coordinate to crop the image to

    Return:
        {}

    Raises:
        AccessError: The token is invalid.
        InputError: The given img_url is valid or returns a HTTP status other 
        than 200, or any of x_start, y_start, x_end, y_end are not within the 
        dimensions of the image at the URL, or the image uploaded is not a JPG.
    '''

    # invalid token
    session = data.session_search("token", token)
    if not session:
        raise AccessError(description='Invalid token')

    # HTTP status other than 200
    try:
        photo = requests.get(img_url)
    except:
        raise InputError(description='Invalid image url.')
    if photo.status_code != 200:
        raise InputError(description='Image could not be found.')

    # save image locally in directory /src/static/ as 'image.jpg'
    try:
        urllib.request.urlretrieve(img_url, "./src/static/image.jpg")
        image = Image.open("./src/static/image.jpg")
    except:
        raise InputError(description='Image could not be found.')

    # image is not a jpg
    image_formats = ["JPEG"]
    if image.format not in image_formats:
        raise InputError(description='Image is not a JPG.')

    # check given bounds to crop image
    (width, height) = image.size
    if x_start < 0 or y_start < 0 or x_end < 0 or y_end < 0:
        raise InputError(description='Negative image dimensions are not allowed.')
    if x_start >= x_end or x_start > width or x_end > width:
        raise InputError(description='Cropping beyond image dimensions.')
    if y_start >= y_end or y_start > height or y_end > height:
        raise InputError(description='Cropping beyond image dimensions.')

    # generate unique filename, crop and save the photo 
    profile_img_url = "static/" + uuid.uuid4().hex + ".jpg"
    filename = "src/" + profile_img_url
    cropped_image = image.crop((x_start, y_start, x_end, y_end))
    cropped_image.save(filename)
    
    # does nothing if no server is running
    try:
        data.update_account(session['u_id'], 'profile_img_url', request.host_url + profile_img_url)
    except:
        pass

    return {
    }
