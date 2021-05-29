# list containing information of all users, sessions, channels, messages etc
# each dictonary represents an object/instance
# data structure is like below

"""
# List containing users info.
users = [
    {
        'u_id': 123,
        'email': 'jack@gmail.com',
        'name_first': 'brian',
        'name_last': 'jack',
        'password': '123',
        'handle_str': 'jackbrian',
        'is_global_owner': True,
        'profile_img_url': 'imgurl/adfnajnerkn23k4234.jpg',
    },
]

# List containing active tokens.
sessions = [
    {
        'token': '123456',
        'u_id': 12
    },
]

# List containing channels info.
channels = [
    {
        'channel_id': 1,
        'name': 'channel1',
        'owner_members': [],
        'all_members': [],
        'messages': [],
        'is_public': True,
    },
]

# Messages list structure
messages = [
    {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': time,
        'reacts': [],
        'is_pinned': False,
    },
]

# Reacts list structure
reacts = [
    {
        'react_id': 0,
        'u_ids': [list of u_id],
        'is_user_reacted' : False
    },
]

# Standups list structure
standups = [
    {
        'c_id': 0,
        'time_finish': time_finish,
        'msg_buffer': [(handle, message)], 
    },
]

# List containing email address waiting to reset password
reset_list = [
    {
        'email': 'email@gmail.com',
        'reset_code': 111111
    }
]
"""

import json
from json import dumps
from threading import Lock

#-------------------------------statistic of how many users registered------------------------------
u_id_stat = 0
channel_id_stat = 0

#----------------------------------------------host url---------------------------------------------
url = ""

#----------------------------------------------database----------------------------------------------
users = []
sessions = []
channels = []
react_ids = [1] # a list of react_id's 

#----------------------------------------------reset_code---------------------------------------------
reset_list = []

#----------------------------------------------standup data------------------------------------------
standups = []
s_lock = Lock()

#----------------------------------------------message data------------------------------------------
message_id_stat = 0

#-------------------------------------method of handling user data------------------------------------
def account_search(key, value):
    '''
    Search for an user based on given key.
    Args: key and corresponding value
    Return: an account if found
    '''

    global users
    account = {}
    for account in users:
        if account[key] == value:
            return account

def is_global_owner(u_id):
    '''
    Given u_id return if it's a global owner of flockr.
    Args: u_id
    Return: True if it's global owner, else False
    '''

    account = account_search("u_id", u_id)
    if account and account['is_global_owner']:
        return True
    else:
        return False

def set_global_permissions(u_id, permission_id):
    ''' Given the user's u_id and new permission_id, reset their permissions. '''

    account = account_search('u_id', u_id)
    
    if permission_id == 1:
        account['is_global_owner'] = True
    else:
        account['is_global_owner'] = False

def new_account(account):
    '''
    Creates a new account, increments u_id_stat and returns new u_id_stat.
    Args: account
    Return: u_id_stat after increment
    '''

    global u_id_stat
    global users
    u_id_stat += 1
    account['u_id'] = u_id_stat
    # check if this is the first user who register
    if u_id_stat == 1:
        account['is_global_owner'] = True
    else:
        account['is_global_owner'] = False
    users.append(account)
    return u_id_stat

def update_account(u_id, key, value):
    '''
    Update certain piece of info of user profile
    Args: u_id, key and corresponding value
    '''
    global users
    account = account_search("u_id", u_id)
    account[key] = value
    user_info_sync(u_id, key, value)

def reset_list_add(email, code):    # pragma: no cover
    '''
    add a new member to reset list
    Args: email and reset code
    '''

    reseter = reset_list_search("email", email)
    if reseter:
        return reseter["reset_code"]
    else:
        new_reset = {
            "email": email,
            "reset_code": code
        }
        reset_list.append(new_reset)
        return code


def reset_list_remove(code):    # pragma: no cover
    '''
    remove a member from reset list
    Args: reset code
    '''
    reset_list.remove(reset_list_search("reset_code", code))

def reset_list_search(key, value):   # pragma: no cover
    '''
    search for a member of reset list based on given key and value
    Args: key and corresponding value
    Return: reset member
    '''
    for reset in reset_list:
        if reset[key] == value:
            return reset
    return {}

def host_update(host_url):   # pragma: no cover
    '''
    upload host url when flask restarts
    '''

    global url
    url = host_url

def img_url_update():    # pragma: no cover
    '''
    update url for every user according to new port
    Args: new address of localhost
    '''

    global users
    global channels
    for user in users:
        # cut the url into protocol + host + local
        url_frac =  user['profile_img_url'].split("/")
        # recombine with different host
        user['profile_img_url'] = url + url_frac[3] + "/" + url_frac[4]
    
    for channel in channels:
        for all_member in channel["all_members"]:
            all_member["profile_img_url"] = account_search("u_id", all_member["u_id"])["profile_img_url"]
        for owner_member in channel["owner_members"]:
            owner_member["profile_img_url"] = account_search("u_id", owner_member["u_id"])["profile_img_url"]

def user_info_sync(u_id, key, value):   # pragma: no cover
    '''
    synchronize user's uptodate info with channels
    Args: u_id, key and corresponding value
    '''
    global channels
    # if the user is one of a channel's normal member
    all_channels = channels_search("all_members", u_id)
    for channel in all_channels:
        for member in channel["all_members"]:
            if member["u_id"] == u_id:
                member[key] = value
    
    # if the user is one of channel's owners
    all_channels = channels_search("owner_members", u_id)
    for channel in all_channels:
        for member in channel["owner_members"]:
            if member["u_id"] == u_id:
                member[key] = value

def add_img_url(u_id, host_url):     # pragma: no cover
    '''
    Add local host to the profile_img_url.
    '''

    account_search("u_id", u_id)["profile_img_url"] = host_url + 'static/default_img.jpg'

#-------------------------------methods for handling session data-----------------------------------
def session_search(key, value):
    ''' 
    Search for active session based on given key and value
    Arg: key and value
    Return: session
    '''
    global sessions
    session = {}
    for session in sessions:
        if session[key] == value:
            return session

def new_session(session):
    '''
    Add a new session to database
    Args: session
    '''
    global sessions
    sessions.append(session)

def delete_session(session):
    '''
    Delete a session from database
    Args: session
    '''
    global sessions
    sessions.remove(session)

def make_user(u_id):
    ''' Returns user given u_id. '''

    account = account_search('u_id', u_id)
    user = {
        'u_id': u_id,
        'email': account['email'],
        'name_first': account['name_first'],
        'name_last': account['name_last'],
        'handle_str': account['handle_str'],
    }
    # adjust for implementation test and route test
    try:
        user['profile_img_url'] = account['profile_img_url']
    except:
        pass
    return user

def users_info():
    ''' Returns a list of all accounts as user. '''

    global users
    users_list = []
    for user in users:
        users_list.append(make_user(user['u_id']))

    return users_list

#----------------------------methods for handling channel data-------------------------------
def make_member(u_id):
    ''' Takes u_id and returns member '''
    account = account_search('u_id', u_id)
    member = {
        'u_id': u_id,
        'name_first': account['name_first'],
        'name_last': account['name_last'],
    }
    try:
        member['profile_img_url'] = account['profile_img_url']
    except:
        pass
    return member

def make_channel(channel_id):
    '''
    Takes channel_id and returns channel which
    has the same structure as one dictionary from channels.
    '''
    channel_full = channels_search('channel_id', channel_id)
    channel = {
        'channel_id': channel_id,
        'name': channel_full['name'],
    }
    return channel

def new_channel(channel_name, u_id, is_public):
    ''' Add new channel and returns channel_id. '''
    global channels
    global channel_id_stat
    member = make_member(u_id)
    channel_id = channel_id_stat
    channel_id_stat += 1
    channels.append(
        {
        'channel_id': channel_id,
        'name': channel_name,
        'owner_members': [member],
        'all_members': [member],
        'messages': [],
        'is_public': is_public,
        }
    )
    return channel_id

def delete_channel(channel):
    ''' Delete a channel. '''
    global channels 
    channels.remove(channel)

def add_member(channel_id, member):
    ''' Add member to channel. '''
    global channels
    channels_search('channel_id', channel_id)['all_members'].append(member)

def promote_owner(channel_id, member):
    ''' Promote an existing member to owner of channel. '''
    global channels
    channels_search('channel_id', channel_id)['owner_members'].append(member)

def remove_member(channel_id, u_id):
    ''' Remove a member from the channel. '''
    global channels
    channel = channels_search('channel_id', channel_id)
    
    # search for this member (could as well be an owner)
    for member in channel["all_members"]:
        if member['u_id'] == u_id:

            # if the member is an owner, delete ownership as well
            if member in channel["owner_members"]:
                channel["owner_members"].remove(member)
            channel["all_members"].remove(member)
    
    # if there's no more owner
    if channel["owner_members"] == []:
        next_member = channel["all_members"][0]
        # if there's no member left, delete the whole channel
        if not next_member:
            channels.remove(channel)
        
        # if there's member left, make this dude new owner
        else:
            channel["owner_members"].append(next_member)
 
def remove_ownership(channel_id, u_id):
    ''' Remove an owner from the channel. '''
    global channels
    channel = channels_search('channel_id', channel_id)
    for member in channel["owner_members"]:
        if member['u_id'] == u_id:
            channel["owner_members"].remove(member)

 
def channels_search(key, value):
    '''
    If key is channel_id return the single channel with matching channel_id or {}.
    If key is owner_members or all_members, return a list of all channels that
    the user with u_id value is a part of (can be the empty list if no results).
    If any other key is used return {}.
    '''
    
    global channels
    if key in ['owner_members', 'all_members']:
        result = []
        for channel in channels:
            for member in channel[key]:
                if member['u_id'] == value:
                    result.append(channel)
                    break
        return result
            
    elif key == 'channel_id':
        for channel in channels:
            if channel[key] == value:
                return channel
    return {}

def is_member(u_id, channel_id):
    ''' Check if given token belongs to one of this channel's members. '''
    global channels
    channel = channels_search('channel_id', channel_id)    
    for member in channel['all_members']:
        if member['u_id'] == u_id:
            return True 
    
    return False
    
def is_owner(u_id, channel_id):
    ''' Check if given token belongs to one of this channel's owners. '''
    global channels
    channel = channels_search('channel_id', channel_id)
    for member in channel['owner_members']:
        if member['u_id'] == u_id:
            return True 
    return False

def is_channel_public(channel_id):
    ''' Check whether or not a channel is public given the channel_id. '''
    channel = channels_search('channel_id', channel_id)
    if channel and channel['is_public']:
        return True
    else:
        return False
    
#------------------------------methods for handling messages data---------------------------------

def add_message(message_id,u_id,message,time,channel_id):
    '''
    Adds a message with "message_id" to a channel with "channel_id" by a user with "u_id" 
    and a timestamp "time".
    '''

    global message_id_stat
    message_insert = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': time,
        'reacts': [],
        'is_pinned': False,
    }

    channel = channels_search('channel_id', channel_id)
    #insert the latest message at the beggining of the list
    channel['messages'].insert(0, message_insert)
    #increment the number of messages in the server.
    message_id_stat += 1

def add_later(message_id, u_id, message, time, channel_id):
    '''
    Add a message with the given time. 
    '''

    message_insert = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_created': time,
        'reacts': [],
        'is_pinned': False,
    }

    channel = channels_search('channel_id', channel_id)
    # if the channel has been deleted, dont add the message
    if channel == {}:
        return
    #insert the latest message at the beggining of the list
    channel['messages'].insert(0, message_insert)

def remove_message(message_id):
    ''' Takes message_id and removes the message from the channel. '''
    (channel, _) = message_search(message_id)
    for message in channel['messages']:
        if (message['message_id'] == message_id):
            channel['messages'].remove(message)
            return

def message_search(message_id):
    '''
    Given message_id, returns (channel, message) where message is the dictionary containing
    message_id, and channel is the dictionary containing the message.
    If no message is found associated with message_id or no channels exist, returns None.
    '''

    global channels
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return (channel, message)

def set_message_react_status(u_id, return_messages):
    '''reacts is List of dictionaries, where each dictionary contains 
    types { react_id, u_ids, is_this_user_reacted } 
    where react_id is the id of a react, 
    and u_ids is a list of user id's of people who've reacted for that react.
    is_this_user_reacted is whether or not the 
    authorised user has been one of the reacts to this post
    '''

    # rd = {'react_id' : 1,'uids' : [], 'is_this_user_reacted' : False}
    
    for m in return_messages:
        if (not m['reacts'] == []):
            for r in m['reacts']:
                if u_id in r['u_ids']:
                    r['is_this_user_reacted'] = True
                else:
                    r['is_this_user_reacted'] = False
    
    return return_messages
    

def message_react_to(u_id, message_id, react_id):
    '''
    React to a message given the message_id by adding the user given by user_id
    to the list of users reacted. 
    '''

    (_, m) = message_search(message_id)

    reacts = m['reacts']
    
    # if there are no reacts for this message
    if reacts == []:
        react = {
            'react_id' : react_id,
            'u_ids' : [u_id],
            'is_this_user_reacted' : False
        }
        reacts.append(react)
        return {}
    
    # if there are reacts to this message
    for r in reacts:
        if react_id == r['react_id']:
            r['u_ids'].append(u_id)
            r['is_this_user_reacted'] = False
            return{}

def message_unreact_to(u_id, message_id, react_id):
    '''
    Unreact a message given the message_id by removing the user given by user_id
    from the list of users reacted. 
    '''

    (_, message) = message_search(message_id)

    for r in message['reacts']:
        if react_id == r['react_id']:
            r['u_ids'].remove(u_id)
            r['is_this_user_reacted'] = False
            return {}  

#---------------------------Functions for standups.------------------------------
def standup_create(channel_id, time_finish):
    '''
    Given channel_id and time_finish, create a standup with these details
    and append it to the standup data structure.
    '''
    global standups
    with s_lock:
        standup = {
            'channel_id': channel_id,
            'time_finish': time_finish,
            'msg_buffer': [], 
        }
        standups.append(standup)
    
def standup_search(channel_id):
    '''
    Given a channel_id, search for and return the standup with channel_id 
    channel_id.
    '''
    global standups
    with s_lock:
        for standup in standups:
            if standup['channel_id'] == channel_id:
                return standup
    return {}
    
def standup_remove(channel_id):
    '''
    Given a channel_id, remove the standup with channel_id channel_id
    from standups.
    '''
    global standups
    with s_lock:
        for (i, standup) in enumerate(standups):
            if standup['channel_id'] == channel_id:
                del standups[i]
                
def standup_message_add(channel_id, handle, message):
    '''
    Given a channel_id, a user handle and a message (str), add the message 
    to the standup running on channel with channel_id channel_id.
    '''
    global standups
    with s_lock:
        for (i, standup) in enumerate(standups):
            if standup['channel_id'] == channel_id:
                standups[i]['msg_buffer'].append((handle, message))

#---------------------------downloading and uploading from database------------------------------
def load(filename):
    '''
    Update program memory with persistent database
    if database is empty or does not exist, nothing will be done.
    Args: filename of database
    '''

    global u_id_stat
    global channel_id_stat
    global message_id_stat
    global users
    global sessions
    global channels
    global reset_list
    try:
        with open(filename, 'r') as FILE:   
            database = json.load(FILE)
            if database:
                u_id_stat = int(database["u_id_stat"])
                channel_id_stat = int(database["channel_id_stat"])
                message_id_stat = int(database["message_id_stat"])
                users = database["users"]
                sessions = database["sessions"]
                channels = database["channels"]
                reset_list = database["reset_list"]
    except Exception:
        pass

# dump data into given file
def save(filename):
    '''
    Upload all the data in memory to persistent database,
    if database does not exist, create one.
    Args: filename of database
    '''

    with open(filename, 'w') as FILE:
        data_collection = {
            "u_id_stat": u_id_stat,
            "channel_id_stat": channel_id_stat,
            "message_id_stat": message_id_stat,
            "users": users,
            "sessions": sessions,
            "channels": channels,
            "reset_list": reset_list
        }
        json.dump(data_collection, FILE)
