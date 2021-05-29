from error import AccessError, InputError
from flask_mail import Mail, Message
from flask import Flask, request, send_from_directory
from json import dump, dumps
from flask_cors import CORS
from os import utime
from datetime import datetime as dt, timezone, timedelta
import base64
import random
import sys
import user
import auth
import data
import json
import other
import channels
import channel
import message
import standup

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
APP.config.update(
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = 'flockr.comp1531.orange5@gmail.com',
	MAIL_PASSWORD = base64.b64decode("SHY0VSM5ZnFwJmQwQQ==").decode("utf-8"),
	MAIL_DEFAULT_SENDER = 'flockr.comp1531.orange5@gmail.com'
)
CORS(APP)
mail = Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#------------------------------------routes for auth.py-------------------------------------
@APP.before_first_request
def init():
    '''
    load database into memory
    update host url
    save status
    '''
    data.load("src/database.json")
    data.host_update(request.host_url)
    data.img_url_update()
    data.save("src/database.json")

@APP.route("/auth/login", methods=['POST'])
def login():
    '''
    Given a registered users' email and password and generates a valid token for 
    the user to remain authenticated.
    Return { u_id, token }.
    '''
    input = request.get_json()
    output = auth.auth_login(input['email'], input['password'])
    data.save("src/database.json")
    return dumps(output)

@APP.route("/auth/logout", methods=['POST'])
def logout():
    '''
    Given an active token, invalidates the token to log the user out. If a valid 
    token is given, and the user is successfully logged out, it returns true, 
    otherwise false.
    Return { is_success }.
    '''
    input = request.get_json()
    output = auth.auth_logout(input['token'])
    data.save("src/database.json")
    return dumps(output)

@APP.route("/auth/register", methods=["POST"])
def register():
    '''
    Given a user's first and last name, email address, and password, create a 
    new account for them and return a new token for authentication in their 
    session. 
    Return { u_id, token }.
    '''
    input = request.get_json()
    output = auth.auth_register(input['email'], input['password'], input['name_first'], input['name_last'])
    data.add_img_url(output["u_id"], request.host_url)
    data.save("src/database.json")
    return dumps(output)

@APP.route('/auth/passwordreset/request', methods=["POST"])
def send_mail():
    '''
    Given an email, raise a request to change the password of the account associated with this email
    Args: email
    Dumps: {reset_code} if email successfully sent, otherwise {}
    '''
    email = request.get_json()["email"]
    account = data.account_search("email", email)
    if account:
        code = data.reset_list_add(email, str(random.randint(100000,1000000)))
        try:
            msg = Message(f"Flockr: Reset password for {account['email']}",
            recipients=[email])
            msg.html = f"<h1>Password Reset</h1>\n<p>Dear {account['name_first'].capitalize()} {account['name_last'].capitalize()}, your reset code is <strong>{code}</strong>, please enter this code in flockr to verify your identity. Thank you.</p>"
            mail.send(msg)
            data.save("src/database.json")
            return dumps ({
                "reset_code": code
            })
        except Exception:
            return dumps ({})
            
@APP.route('/auth/passwordreset/reset', methods=["POST"])
def password_reset():
    input = request.get_json()
    output = auth.auth_setpassword(input["reset_code"], input["new_password"])
    data.save("src/database.json")
    return dumps(output)

#-----------------------------------routes for other.py----------------------------------------
@APP.route('/clear', methods=['DELETE'])
def clear():
    '''
    Clear all the data exist in memory and database
    Return {}.
    '''
    other.clear()
    data.save("src/database.json")
    return {}

@APP.route('/users/all', methods=['GET'])
def users_all():
    '''
    Provides a list of all users and their details.
    Return { users }. 
    '''
    token = request.args.get('token')
    users = other.users_all(token)
    return dumps(users)

@APP.route('/admin/userpermission/change', methods=['POST'])
def admin_user_permission_change():
    '''
    Given a User by their user ID, set their permissions to new permissions 
    described by permission_id.
    Return {}.
    '''
    payload = request.get_json()
    token = payload['token']
    u_id = int(payload['u_id'])
    permission_id = payload['permission_id']
    output = other.admin_userpermission_change(token, u_id, permission_id)
    data.save("src/database.json")
    return dumps(output)
    
@APP.route('/search', methods=['GET'])
def other_search():
    '''
    Given a query string, return all messages containing that
    query string.
    Return { messages }.
    '''
    payload = request.args
    token = payload['token']
    query_str = payload['query_str']
    output = other.search(token, query_str)
    data.save("src/database.json")
    return dumps(output)

#------------------------------------routes for user.py-------------------------------------
@APP.route("/user/profile", methods=["GET"])
def profile():
    '''
    For a valid user, returns information about their user_id, email, first name, 
    last name, and handle.
    Return { user }.
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    output = user.user_profile(token, u_id)
    return dumps(output)

@APP.route("/user/profile/setname", methods=["PUT"])
def profile_setname():
    '''
    Update the authorised user's first and last name.
    Return {}.
    '''
    input = request.get_json()
    output = user.user_profile_setname(input['token'], input['name_first'], input['name_last'])
    data.save("src/database.json")
    return dumps(output)

@APP.route("/user/profile/setemail", methods=["PUT"])
def profile_setemail():
    '''
    Update the authorised user's email address.
    Return {}.
    '''
    input = request.get_json()
    output = user.user_profile_setemail(input['token'], input['email'])
    data.save("src/database.json")
    return dumps(output)

@APP.route("/user/profile/sethandle", methods=["PUT"])
def profile_sethandle():
    '''
    Update the authorised user's handle (i.e. display name).
    Return {}.
    '''
    input = request.get_json()
    output = user.user_profile_sethandle(input['token'], input['handle_str'])
    data.save("src/database.json")
    return dumps(output)

@APP.route("/user/profile/uploadphoto", methods=["POST"])
def profile_uploadphoto():
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). 
    Return {}.
    '''
    photo = request.get_json()
    token = photo['token']
    img_url = photo['img_url']
    x_start = int(photo['x_start'])
    y_start = int(photo['y_start'])
    x_end = int(photo['x_end'])
    y_end = int(photo['y_end'])
    
    output = user.user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    data.save("src/database.json")

    return dumps(output)

@APP.route('/static/<path:path>')
def serve_image(path):
    return send_from_directory('', path)

#----------------------------------routes for channels.py--------------------------------------
@APP.route('/channels/create', methods=['POST'])
def channels_create():
    '''
    Creates a new channel with that name that is either a public or private 
    channel.
    Return { channel_id }.
    '''
    payload = request.get_json()
    channel = channels.channels_create(payload['token'], payload['name'], bool(payload['is_public']))
    data.save('src/database.json')
    return dumps(channel)

@APP.route('/channels/listall', methods=['GET'])
def channels_listall():
    '''
    Provide a list of all channels (and their associated details).
    Return { channels }.
    '''
    token = request.args.get('token')
    channels_list = channels.channels_listall(token)
    return dumps(channels_list)
    
@APP.route('/channels/list', methods=['GET'])
def channels_list():
    '''
    Provide a list of all channels (and their associated details) 
    that the authorised user is part of.
    Return { channels }.
    '''
    token = request.args.get('token')
    channels_list = channels.channels_list(token)
    return dumps(channels_list)

#----------------------------------routes for channel.py---------------------------------------
@APP.route('/channel/details', methods=['GET'])
def channel_details():
    '''
    Get the details of a channel given a token and channel_id.
    Return { name, owner_members, all_members }.
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    details = channel.channel_details(token, channel_id)
    return dumps(details)

@APP.route('/channel/invite', methods=['POST'])
def channel_invite():  
    '''
    Invite a user to a channel given a token, channel_id, and u_id.
    Return {}.
    '''
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    u_id = int(payload['u_id'])
    output = channel.channel_invite(token, channel_id, u_id)
    data.save('src/database.json')
    return dumps(output)

@APP.route('/channel/join', methods=['POST'])
def channel_join():
    '''
    Join a channel given a token and channel_id.
    Return {}.
    '''
    payload = request.get_json()
    token = payload['token']
    channel_id = int(payload['channel_id'])
    output = channel.channel_join(token, channel_id)
    data.save('src/database.json')
    return dumps(output)
    
@APP.route('/channel/leave', methods=['POST'])
def channel_leave():
    ''' 
    Remove user with token 'token' from channel with channel id 'channel_id'
    input arguments: token, channel_id
    return{}
    ''' 
    payload = request.get_json()
    output = channel.channel_leave(payload['token'], int(payload['channel_id']))
    data.save('src/database.json')
    return dumps(output)
    
@APP.route('/channel/addowner', methods=['POST'])
def channel_addowner():
    '''
    Add a user with u_id u_id to owner of a channel with channel_id channel_id
    when given the valid token of an owner of the channel or global owner of the
    Flockr.
    Return {}.
    '''
    payload = request.get_json()
    output = channel.channel_addowner(payload['token'], int(payload['channel_id']), 
    int(payload['u_id']))
    data.save('src/database.json')
    return dumps(output)
    
@APP.route('/channel/removeowner', methods=['POST'])
def channel_removeowner():
    '''
    Remove a user with u_id u_id to owner of a channel with channel_id 
    channel_id when given the valid token of an owner of the channel or global 
    owner of the Flockr.
    Return {}
    '''
    payload = request.get_json()
    output = channel.channel_removeowner(payload['token'], 
        int(payload['channel_id']), int(payload['u_id']))
    data.save('src/database.json')
    return dumps(output)

@APP.route('/channel/messages', methods=['GET'])
def channel_messages():
    '''
    Retrieve the latest messages in a channel.
    takes in a valid token, a valid channel_id and a start int
    return a dictionary with a start, end and list of (end - start) messages
    return end as -1 if less that 50 messages left in the channel

    return {
        'messages': [],
        'start': start,
        'end': end,
    }
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    messages = channel.channel_messages(token,channel_id,start)
    return dumps(messages)

#----------------------------------routes for message.py--------------------------------------
@APP.route('/message/send', methods=['POST'])
def message_send():
    '''
    Send a message from authorised_user to the channel specified by channel_id
    input arguments: token, channel_id, message
    return {message_id}
    '''

    payload = request.get_json()
    message_id = message.message_send(payload['token'], int(payload['channel_id']), payload['message'])
    data.save('src/database.json')
    return dumps(message_id)

@APP.route('/message/remove', methods=['DELETE'])
def message_remove():
    '''
    Given a message_id for a message, this message is removed from the channel.
    Return {}.
    '''
    payload = request.get_json()
    message_value = message.message_remove(payload['token'], int(payload['message_id']))
    return dumps(message_value)
    
@APP.route('/message/edit', methods=['PUT'])
def message_edit():
    '''
    Given an authorized token, a message_id and a string message, change the
    message with message_id message_id to have message message.
    Return {}.
    '''
    payload = request.get_json()
    output = message.message_edit(payload['token'], int(payload['message_id']), 
        payload['message'])
    data.save('src/database.json')
    return dumps(output)

@APP.route('/message/pin', methods=['POST'])
def message_pin():
    """
    Given a message within a channel, mark it as "pinned" 
    to be given special display treatment by the frontend
    """

    payload = request.get_json()
    pin_return = message.message_pin(payload['token'], int(payload['message_id']))
    data.save('src/database.json')
    return dumps(pin_return)

@APP.route('/message/unpin', methods=['POST'])
def message_unpin():
    """ Given a message within a channel, remove its mark as unpinned """

    payload = request.get_json()
    unpin_return = message.message_unpin(payload['token'], int(payload['message_id']))
    data.save('src/database.json')
    return dumps(unpin_return)

@APP.route('/message/react', methods=['POST'])
def message_react():
    '''
    Given a message within a channel the authorised user is part of, 
    add a "react" to that particular message.
    '''
    payload = request.get_json()
    react = message.message_react(payload['token'],int(payload['message_id']), int(payload['react_id']))
    data.save('src/database.json')
    return dumps(react)

@APP.route('/message/unreact', methods=['POST'])
def message_unreact():
    '''
    Given a message within a channel the authorised user is part of, 
    remove a "react" to that particular message.
    '''
    payload = request.get_json()
    unreact = message.message_unreact(payload['token'],int(payload['message_id']), int(payload['react_id']))
    data.save('src/database.json')
    return dumps(unreact)



@APP.route('/message/sendlater', methods=['POST'])
def message_sendlater():
    '''
    Send a message from authorised_user to the channel 
    specified by channel_id automatically at a specified time in the future
    '''
    payload = request.get_json()
    token = payload['token']
    c_id = int(payload['channel_id'])
    m = payload['message']
    send_time = int(payload['time_sent'])

    to_send = message.message_sendlater(token, c_id, m, send_time)
    data.save('src/database.json')
    return dumps(to_send)


#------------------------------routes for standup-------------------------------
@APP.route('/standup/start', methods=['POST'])
def standup_start():
    """
    Start a standup of specified length (seconds) on channel
    with channel_id channel_id.
    """
    payload = request.get_json()
    time_finish = standup.standup_start(payload['token'], int(payload['channel_id']),
        int(payload['length']))
    data.save('src/database.json')
    return dumps(time_finish)
    
@APP.route('/standup/active', methods=['GET'])
def standup_active():
    """
    Check if a standup is active and if so when that standup finishes when
    given the channel_id of a valid channel.
    """
    payload = request.args
    result = standup.standup_active(payload['token'], int(payload['channel_id']))
    data.save('src/database.json')
    return dumps(result)
    
@APP.route('/standup/send', methods=['POST'])
def standup_send():
    """
    Send a message to a standup running on channel with a given channel_id
    to be buffered until the standup ends.
    """
    payload = request.get_json()
    output = standup.standup_send(payload['token'], int(payload['channel_id']),
    payload['message'])
    data.save('src/database.json')
    return dumps(output)

if __name__ == "__main__":
    APP.run(port=0)
