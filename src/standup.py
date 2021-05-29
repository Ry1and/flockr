import data
from datetime import timezone, datetime
from message import message_send
from time import sleep
from error import AccessError, InputError
from threading import Timer

open_timers = []

def standup_close(u_id, channel_id):
    '''
    Close the standup on the channel with channel_id channel_id
    
    Args:
        c_id (int): c_id of the standup to be closed.
        duration (int): duration after which to close the standup (seconds).
        
    Return:
        None
        
    Raises:
        NA
    '''
    
    standup = data.standup_search(channel_id)
    message = ''
    for msg in standup['msg_buffer']:
        message += f"\n{msg[0]}: {msg[1]}"
    
    if message != '':
        message = message[1:]
        # Note: Needs to be added directly since the message should still be
        # sent even if the user is logged out in the middle of the standup.
        time = int(datetime.utcnow().replace(tzinfo = timezone.utc).timestamp())
        data.add_message(data.message_id_stat, u_id, message, time, channel_id)
    
    data.standup_remove(channel_id)
    
def standup_cancel_timers():
    '''
    Cancel all currently waiting timers started by standup_start.
    
    Args:
        NA
        
    Return:
        None
        
    Raises:
        NA
    '''
    
    global open_timers
    
    for timer in open_timers:
        timer.cancel()
    open_timers = []
        
def standup_start(token, channel_id, length):
    '''
    Start a standup on channel with channel_id channel_id of length length 
    (seconds).
    
    Args:
        token (str): token of user calling this function.
        channel_id (int): channel_id of channel to have standup started on.
        length (int): duration of standup in seconds.
        
    Return:
        time_finish (timestamp): time the standup will end.
        
    Raises:
        AccessError: token is not valid.
        InputError: channel_id does not belong to a valid channel or there is
            already an active standup running on the channel with channel_id
            channel_id.
    '''
    
    global open_timers
    
    # Checks for invalid token
    session = data.session_search('token', token)
    if session == None:
        raise AccessError(description = 'Invalid token.')
        
    # Checks that channel_id belongs to a valid channel.
    if data.channels_search('channel_id', channel_id) == {}:
        raise InputError(description = 'Channel does not exist.')
        
    # Checks that there is not already a standup running on the channel.
    standup = data.standup_search(channel_id)
    if standup != {}:
        raise InputError(description = 'Standup already active.')
        
    # Calculate end_time and add the standup.
    timestamp = int(datetime.utcnow().replace(tzinfo = timezone.utc).timestamp())
    time_finish = timestamp + length
    data.standup_create(channel_id, time_finish)
        
    # Start the timer to close the standup at the appropriate time.
    if length <= 0: length = 0
    close_timer = Timer(length, standup_close, [session['u_id'], channel_id])
    close_timer.daemon = True
    open_timers.append(close_timer)
    close_timer.start()
    
    return {'time_finish': time_finish}
    
def standup_active(token, channel_id):
    '''
    Returns whether a standup is active on the channel with channel_id
    channel_id and when the standup ends.
    
    Args:
        token (str): token of user calling this function.
        channel_id (int): channel_id of channel to have standup started on.
        
    Return:
        is_active (bool): if there is a standup active on the channel with 
            channel_id channel_id.
        time_finish (timestamp): time said standup will end or None if no
            is_active is false.
        
    Raises:
        AccessError: token is not valid.
        InputError: channel_id does not belong to a valid channel.
    '''
    
    # Checks for invalid token
    if data.session_search('token', token) == None:
        raise AccessError(description = 'Invalid token.')
        
    # Checks that channel_id belongs to a valid channel.
    if data.channels_search('channel_id', channel_id) == {}:
        raise InputError(description = 'Channel does not exist.')
    
    standup = data.standup_search(channel_id)
    if standup == {}:
        result = {'is_active': False, 'time_finish': None}
    else:
        result = {'is_active': True, 'time_finish': standup['time_finish']}
    return result
    
def standup_send(token, channel_id, message):
    '''
    Returns whether a standup is active on the channel with channel_id
    channel_id and when the standup ends.
    
    Args:
        token (str): token of user calling this function.
        channel_id (int): channel_id of channel to have standup started on.
        message (str): message to be buffered in standup.
        
    Return:
        {}
        
    Raises:
        AccessError: token is not valid or belongs to a user who is not a member
            of the channel with channel_id channel_id.
        InputError: channel_id does not belong to a valid channel, message is
            more than 1000 chars in length or an active standup is not running
            on the channel with channel_id channel_id.
    '''
    
    # Checks for invalid token
    session = data.session_search('token', token)
    if session == None:
        raise AccessError(description = 'Invalid token.')
        
    # Checks that channel_id belongs to a valid channel.
    channel = data.channels_search('channel_id', channel_id)
    if channel == {}:
        raise InputError(description = 'Channel does not exist.')
    
    # Check that the user is a member of the channel.
    is_member = False
    for member in channel['all_members']:
        if member['u_id'] == session['u_id']:
            is_member = True
            break
    if not is_member:
        raise AccessError (description = 'User is not a member of this channel.')
    
    # Message is not more than 1000 chars.
    if len(message) > 1000:
        raise InputError (description = 'Message is over 1000 chars in length.')
    
    # Checks that there is not already a standup running on the channel.
    standup = data.standup_search(channel_id)
    if standup == {}:
        raise InputError(description = 'Standup not active.')
        
    handle = data.account_search('u_id', session['u_id'])['handle_str']
    data.standup_message_add(channel_id, handle, message)
    return {}
    
