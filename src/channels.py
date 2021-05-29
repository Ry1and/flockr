from error import InputError, AccessError
import data

def channels_list(token):
    """
    Provide a list of all channels (and their associated details)
    that the authorised user is part of.
    
    Args:
        token (str): token of user attempting to get list of channels they are in
    
    Return: 
        {channels}

    Raises:
        AccessError: Token is invalid.
    """
    # error check for valid token
    session = data.session_search('token', token)
    if (session == None):
        raise AccessError(description='Token is invalid.')

    # find u_id from token
    u_id = session['u_id']

    channels_list = []

    for channel in data.channels_search('all_members', u_id):
        channels_list.append(data.make_channel(channel['channel_id']))

    return {'channels': channels_list}


def channels_listall(token):
    """  
    Provide a list of all channels (and their associated details)

    Args:
        token (str): token of user attempting to get list of all channels
    
    Return: 
        {channels}

    Raises:
        AccessError: Token is invalid.
    """
    # error check for valid token
    if (data.session_search('token', token) == None):
        raise AccessError(description='Token is invalid.')
    
    channels_list = []

    for channel in data.channels:
        channels_list.append(data.make_channel(channel['channel_id']))

    return {'channels': channels_list}

def channels_create(token, name, is_public):
    """
    Creates a new channel with that name that is 
    either a public or private channel

    Args:
        token (str): token of user attempting to create a new channel
        name (str): name of new channel
        is_public (bool): sets the new channel to public (true) or private (false)
    
    Return: 
        {channel_id}

    Raises:
        AccessError: Token is invalid.
        InputError: Channel name is longer than 20 characters.
    """
    # error check for valid token
    session = data.session_search('token', token)
    if (session == None):
        raise AccessError(description='Token is invalid.')
    
    # error check for name longer than 20 characters
    if (len(name) > 20):
        raise InputError(description='Channel name is longer than 20 characters.')

    # find u_id from token
    u_id = session['u_id']

    channel_id = data.new_channel(name, u_id, is_public)

    return {'channel_id': channel_id}
    
