import channel
import channels
import data
from error import AccessError, InputError
from datetime import datetime as dt, timezone
import threading

def message_send(token, channel_id, message):
    '''
    send a message from an authorised user to a valid channel

    Args: 
        token (str): token of user attempting to get list of all channels.
        channel_id(int): The channel_id of the channel to which the message has to be sent.
        message(str): The actual message itself.
    
    Raises:
        AccessError: Token is invalid, user is not a member of the channel.
        InputError: When the message is greater than a 1000 chars, an invalid channel_id is provided.

    Return:
        {'message_id' : message_id}

    '''
    
    # check if the token is valid
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')

    # check if the channel is exists
    if (data.channels_search('channel_id', channel_id) == {}):
        raise InputError(description='This Channel Doesn\'t Exist!')

    # check if the user is a member of the channel
    u_id = data.session_search('token', token)['u_id']
    if (not data.is_member(u_id, channel_id)):
        raise AccessError(description='You Cannot Access This Channel!')

    # check if the message is greater than 1000 chars
    if (len(message) > 1000):
        raise InputError(description='This Message Is TOO Long!')

    # Find the date_time
    send_time = dt.utcnow()
    send_time = int(send_time.replace(tzinfo=timezone.utc).timestamp())

    # Calculate the message_id
    message_id = data.message_id_stat + 1

    data.add_message(message_id,u_id,message,send_time,channel_id)

    return {
        'message_id' : message_id 
    }


def message_remove(token, message_id):
    ''' 
    Given a message_id for a message, this message is removed from the channel. 
    
    Args:
        token (str): token of user attempting to get list of all channels
        message_id (int): message_id of message to be removed
    
    Return: 
        {}

    Raises:
        AccessError: Token is invalid. User is not global owner, not channel owner and not message sender 
        InputError: Message does not exist.
    '''
    
    # error check for valid token
    session = data.session_search('token', token)
    if session is None:
        raise AccessError(description='Token is invalid.')
    
    # error check for if message exists
    m_search = data.message_search(message_id)
    if m_search is None:
        raise InputError(description='Message does not exist.')
    (result_channel, result_message) = m_search
    
    u_id = session['u_id']
    user = data.account_search('u_id', u_id)

    # error check for if user is not global owner, not channel owner, and not message sender 
    if not ((data.make_member(u_id) in result_channel['owner_members']) 
            or user['is_global_owner'] or (result_message['u_id'] == u_id)):
        raise AccessError(description='Need to be global owner, channel owner, or message sender.')

    data.remove_message(message_id)

    return {}

def message_edit(token, message_id, message):

    '''
    Change message with message_id message_id to message. If message is the
    empty string remove the message.
    
    Args:
        token (str): token of user attempting to edit a message.
        message_id (int): message_id of message to be edited.
        message (str): New message string.
        
    Return:
        {}
        
    Raises:
        AccessError: If the token does not belong to an authorized user (sender
        of the message with message_id messsage_id, owner of the channel the
        message was sent to, or global owner of Flockr.)
        InputError: If message with message_id message_id doesn't exist.
    '''

    # Check the user is authorized.
    calling_session = data.session_search('token', token)
    if calling_session == None:
        raise AccessError(description = 'Invalid Token')
    calling_u_id = calling_session['u_id']
    
    # If no message was found raise an input error.
    m_search = data.message_search(message_id)
    if m_search == None:
        raise InputError(description = 'Message does not exist.')
    (result_channel, result_message) = m_search
    
    # Check the calling user is authorized.
    global_owner = data.account_search('u_id', calling_u_id)['is_global_owner']
    channel_owner = (data.make_member(calling_u_id) in result_channel['owner_members'])
    message_sender = (result_message['u_id'] == calling_u_id)
    if not (global_owner or channel_owner or message_sender):
        raise AccessError(description = 'User is not authorized to edit this message.')

    # Edit/remove the message.
    if message == '':
        message_remove(token, result_message['message_id'])
    else:
        result_message['message'] = message
    
    return {}

def message_pin(token, message_id):
    """
    Given a message within a channel, mark it as "pinned" 
    to be given special display treatment by the frontend

    Args:
        token (str): token of user attempting to pin the message.
        message_id (int): message_id of message to be pinned.

    Return:
        {}

    Raises:
        AccessError: Token is invalid. User is not member of channel. User is not owner of channel.
        InputError: Message_id does not exist. Message with message_id is already pinned.
    """
    
    # error check for valid token
    session = data.session_search('token', token)
    if session is None:
        raise AccessError(description='Token is invalid.')

    # error check for if message exists
    m_search = data.message_search(message_id)
    if m_search is None:
        raise InputError(description='Message does not exist.')
    (result_channel, result_message) = m_search

    # error check for if user is member of channel
    channel_id = result_channel['channel_id']
    u_id = session['u_id']
    if not data.is_member(u_id, channel_id):
        raise AccessError(description='User is not member of channel.')

    # error check for if user is owner of channel
    if not data.is_owner(u_id, channel_id):
        raise AccessError(description='User is not owner of channel.')

    # error check for if message is already pinned
    if result_message['is_pinned']:
        raise InputError(description='Message already pinned.')
    
    result_message['is_pinned'] = True

    return {}

def message_unpin(token, message_id):
    """
    Given a message within a channel, remove its mark as unpinned

    Args:
        token (str): token of user attempting to unpin the message.
        message_id (int): message_id of message to be unpinned.

    Return:
        {}

    Raises:
        AccessError: Token is invalid. User is not member of channel. User is not owner of channel.
        InputError: Message_id does not exist. Message with message_id is already unpinned.
    """
    
    # error check for valid token
    session = data.session_search('token', token)
    if session is None:
        raise AccessError(description='Token is invalid.')

    # error check for if message exists
    m_search = data.message_search(message_id)
    if m_search is None:
        raise InputError(description='Message does not exist.')
    (result_channel, result_message) = m_search

    # error check for if user is member of channel
    channel_id = result_channel['channel_id']
    u_id = session['u_id']
    if not data.is_member(u_id, channel_id):
        raise AccessError(description='User is not member of channel.')

    # error check for if user is owner of channel
    if not data.is_owner(u_id, channel_id):
        raise AccessError(description='User is not owner of channel.')

    # error check for if message is already unpinned
    if not result_message['is_pinned']:
        raise InputError(description='Message already unpinned.')
    
    result_message['is_pinned'] = False

    return {}

def message_react(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of, 
    add a "react" to that particular message.

    Args:
        token(str): The token of the user attempting to react to a message.
        message_id(int): The id of the message the user is attempting to react to.
        react_id(int): the id of the reaction-type the user wishes to use.
    

    Return: {}

    Raises: 
        AccessError: When the token is invalid
        InputError: Invalid message_id, invalid react_id, user has already reacted to
        the message
    '''
    
    # invalid token
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')

    # invalid message id
    if not data.message_search(message_id):
        raise InputError(description='Invalid MessageID!')

    # invalid react id
    if react_id not in data.react_ids:
        raise InputError(description='Invalid react_id!')

    
    # if the authorised user has already reacted to this message
    # raise an input error
    u_id = data.session_search('token', token)['u_id']
    (_, message) = data.message_search(message_id)


    for r in message['reacts']:
        if react_id == r['react_id']:
            if u_id in r['u_ids']:
                raise InputError(description='You have already reacted to this message!')
            
    
    
    # add the react
    data.message_react_to(u_id, message_id, react_id)

    return {}


def message_unreact(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of, 
    remove a "react" to that particular message.

    Args:
        token(str): The token of the user attempting to react to a message.
        message_id(int): The id of the message the user is attempting to react to.
        react_id(int): the id of the reaction-type the user wishes to use.
    

    Return: {}

    Raises: 
        AccessError: When the token is invalid
        InputError: Invalid message_id, invalid react_id, user has not already reacted to
        the message
    
    '''

    # invalid token
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')

    # invalid message id
    if not data.message_search(message_id):
        raise InputError(description='Invalid MessageID!')

    # invalid react id
    if react_id not in data.react_ids:
        raise InputError(description='Invalid react_id!')

    # if the authorised user has not already reacted to this message
    # raise an input error
    u_id = data.session_search('token', token)['u_id']
    (_, message) = data.message_search(message_id)
    # print(message)

    if message['reacts'] == []:
        raise InputError(description='You have already reacted to this message!')

    for r in message['reacts']:
        if react_id == r['react_id']:
            if u_id not in r['u_ids']:
                raise InputError(description='You have already reacted to this message!')

    
    data.message_unreact_to(u_id,message_id, react_id)

    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified
    by channel_id automatically at a specified time in the future.

    Args:
        token(str): The token of the user attempting to send the message.
            
        channel_id(int): channel_id of the channel to which the user 
        is trying to send a message to.

        message(str): The actual message itself.

        time_sent(int): The time when the message should be sent.
    
    Return {'message_id':message_id}

    Raises:
        InputError when any of:
            Channel ID is not a valid channel
            Message is more than 1000 characters
            Time sent is a time in the past

        AccessError when:  
            The authorised user has 
            not joined the channel they are trying to post to.
            When the token is invalid
        
    '''

    # invalid token
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')

    # check if the channel is exists
    if (data.channels_search('channel_id', channel_id) == {}):
        raise InputError(description='This Channel Doesn\'t Exist!')

    # check if the user is a member of the channel
    u_id = data.session_search('token', token)['u_id']
    if (not data.is_member(u_id, channel_id)):
        raise AccessError(description='You Cannot Access This Channel!')

    # check if the message is greater than 1000 chars
    if (len(message) > 1000):
        raise InputError(description='This Message Is TOO Long!')

    
    # check if the time_sent is in the future:
    send_time = time_sent
    send_time = dt.fromtimestamp(send_time, tz=timezone.utc)
    # send_time = send_time.replace(tzinfo=None)

    if dt.now(tz=timezone.utc) > send_time:
        raise InputError(description='Invalid Time')

    # find the time difference
    now_time = dt.now(tz=timezone.utc)
    delay_time = int((send_time - now_time).total_seconds())

    data.message_id_stat += 1
    m_id = data.message_id_stat
    
    threading.Timer(delay_time, data.add_later, args=(m_id, u_id, message,time_sent, channel_id)).start()
    
    return {'message_id' : m_id}


