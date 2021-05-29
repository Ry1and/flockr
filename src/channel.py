import sys
import data
import channels
from error import AccessError, InputError

def channel_invite(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with ID channel_id. 
    Once invited the user is added to the channel immediately. 
    
    Args:
        token (str): token of user attempting to invite a user to a channel.
        channel_id (int): channel_id of the channel a user is to be invited to.
        u_id (int): u_id of the user who is to be invited to the channel.

    Return:
        {}

    Raises:
        AccessError: The token does not refer to a current member of the channel 
        with the given channel_id.
        InputError: The channel with the given channel_id or the user with the 
        given u_id does not exist. 
    '''

    # checks for invalid channel id 
    if not data.channels_search('channel_id', channel_id):
        raise InputError(description='Invalid channel id.')
    
    # checks for invalid user (invitee) id
    if not data.account_search('u_id', u_id):
        raise InputError(description='Invalid user_id.')

    # checks for invalid token of inviter
    session = data.session_search('token', token)
    if not session:
        raise AccessError(description='Invalid token.')

    inviter_u_id = session['u_id']
    
    # checks for when user who is inviting is not a member of the channel 
    if not data.is_member(inviter_u_id, channel_id):
        raise AccessError(description='User is not a member of the channel.')

    # no effect if a member is inviting someone already in the channel
    if data.is_member(u_id, channel_id):
        return {
        }

    # add the member to the channel
    member = data.make_member(u_id)
    data.add_member(channel_id, member)

    # global owner is promoted as an owner of the channel
    if data.is_global_owner(u_id):
        data.promote_owner(channel_id, member)

    return {
    }

# Given a channel with ID channel_id that the authorised user is part of, provide 
# basic details about the channel.
def channel_details(token, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is part of, 
    provide basic details about the channel.

    Args: 
        token (str): token of the user attempting to obtain details of a 
        channel.
        channel_id (int): channel_id of the channel a user is obtaining details 
        about.

    Return:
        { name, owner_members, all_members }

    Raises: 
        AccessError: The token does not refer a current member of the channel
        with the given channel_id.
        InputError: The channel with the given channel_id does not exist. 
    '''

    # checks for invalid channel id 
    channel = data.channels_search('channel_id', channel_id)
    if not channel:
        raise InputError(description='Invalid channel id.')
    
    # checks for invalid token
    session = data.session_search('token', token)
    if not session:
        raise AccessError(description='Invalid token.')

    u_id = session['u_id']

    # checks for when user who is getting details is not a member of the channel
    if not data.is_member(u_id, channel_id):
        raise AccessError('User is not a member of the channel.')
    
    c_details = {
        'name': channel['name'], 
        'owner_members': channel['owner_members'], 
        'all_members': channel['all_members']
    }

    return c_details

def channel_messages(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, 
    return up to 50 messages between index "start" and "start + 50".
    Message with index 0 is the most recent message in the channel. 
    This function returns a new index "end" which is the value of "start + 50", 
    or, if this function has returned the least recent messages in the channel, 
    returns -1 in "end" to indicate there are no more messages to load after this return.


    Args: 
        token(str): token of the user attempting to retrieve the messages in a channel.
        channel_id(int): channel_id of the channel from which the user is trying to 
        retrieve the messages.
        start(int): The start position from which the previous messages should be loaded.

    Return: 
        {messages, start, end}
    
    Raises: 
        AccessError: Token is invalid or user is not a member of the channel.
        InputError: When the start index is greater than total number of messages or
        an invalid channel_id is provided.
    '''


    #check if token is invalid
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')


    # check if the channel_id is valid
    if (data.channels_search('channel_id', channel_id) == {}):
        raise InputError(description='This Channel Doesn\'t Exist!')

    # check to see if the user is a member of the channel
    u_id = data.session_search('token', token)['u_id']
    if not (data.is_member(u_id, channel_id)):
        raise AccessError(description='You Cannot Access This Channel!')

    #check if start is a valid number
    channel = data.channels_search('channel_id', channel_id)
    m_length = len(channel['messages'])

    if (start > m_length):
        raise InputError(description='Invalid Message Start Index!')

    all_messages = data.channels_search('channel_id', channel_id)['messages']


    end = start + 50
    if (end > m_length):
        last = m_length
        end = -1
        return_messages = all_messages[start:last]
    else:
        return_messages = all_messages[start:end]

    return_messages = data.set_message_react_status(u_id, return_messages)

    result = {
        'messages': return_messages,
        'start': start,
        'end': end,
    }

    return result

def channel_leave(token, channel_id):
    '''
    Given a channel_id, the user with token "token" is 
    removed as a member of this channel. 
    
    If the user is an owner of the channel, they are 
    removed from both the members_list and the owners_list
    when they leave the channel.

    If the user is the last member of the channel, once they
    leave, the channel is deleted.

    Args: 
        token(str): token of the user attempting to leave the channel.
        channel_id(int): channel_id of the channel the user is 
        attempting to leave.

    Return:
        {}
    
    Raises:
        AccessError: Token is invalid or user is not a member of the channel.
        InputError: When a user tries to leave a channel that doesn't exist.
    '''

    # if token is invalid, raise access error
    if not data.session_search('token', token):
        raise AccessError(description='Invalid Token!')

    #when user tries to leave a channel that doesn't exist
    #InputError
    if (data.channels_search('channel_id', channel_id) == {}):
        raise InputError(description='This Channel Doesn\'t Exist!')
    
    u_id = data.session_search('token', token)['u_id']
    
    #when user tries to leave a channel that they arent in
    #AccessError
    if (not data.is_member(u_id, channel_id)):
        raise AccessError(description='You Cannot Access This Channel!')

    #if user is the last one in the channel, delete the channel
    o_list = data.channels_search('channel_id', channel_id)['owner_members']
    m_list = data.channels_search('channel_id', channel_id)['all_members']
    
    if (len(o_list) == 1 and len(m_list) == 1):
        if (o_list[0]['u_id'] == m_list[0]['u_id'] == u_id):
            channel = data.channels_search('channel_id', channel_id)
            data.delete_channel(channel)
            return {}

    
    # remove the user from the channel
    data.remove_member(channel_id, u_id)

    
    return {}

# Given a channel_id of a channel that the authorised user can join, adds them to
# that channel.
def channel_join(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them 
    to that channel.

    Args:
        token (str): token of the user attempting to join a channel.
        channel_id (int): channel_id of the channel a user is attempting to join.
    
    Return:
        { name, owner_members, all_members }

    Raises:
        AccessError: The channel with the given channel_id refers to a private 
        channel and the user with the given token is not a global owner of Flockr. 
        InputError: The channel with the given channel_id does not exist. 

    '''

    # checks for invalid channel id 
    if not data.channels_search('channel_id', channel_id):
        raise InputError(description='Invalid channel id.')
    
    # checks for invalid token
    session = data.session_search('token', token)
    if not session:
        raise AccessError(description='Invalid token.')
    
    u_id = session['u_id']

    # no effect if a member in a channel is (re-)joining the channel 
    if data.is_member(u_id, channel_id):
        return {
        }

    # user is not a global owner and channel is private
    if not data.is_global_owner(u_id) and not data.is_channel_public(channel_id):
        raise AccessError('Channel is private.')

    # add the member to the channel
    member = data.make_member(u_id)
    data.add_member(channel_id, member)
    
    # global owner is promoted as an owner of the channel
    if data.is_global_owner(u_id):
        data.promote_owner(channel_id, member)

    return {
    }

def channel_addowner(token, channel_id, u_id):

    '''
    Add the user with u_id u_id as an owner of the channel with channel_id
    channel_id.
    
    Args:
        token (str): token of user attempting to add a user as an owner.
        channel_id (int): channel_id of the channel a user is to be added
        as an owner to.
        u_id (int): u_id of the user who is to be added as an owner.
        
    Return:
        {}
        
    Raises:
        AccessError: If the token does not belong to a user who is either an
        owner of the channel with channel_id channel_id or a global owner
        of Flockr.
        InputError: The channel with channel_id channel_id doesn't exist or
        the user with u_id u_id is already an owner of the channel with
        channel_id channel_id.
    '''

    # First get the channel if it exists.
    channel = data.channels_search('channel_id', channel_id)
    if channel == {}:
        raise InputError(description = 'Channel does not exist.')
    
    # Check that the user with u_id is not already an owner of the channel.
    if data.is_owner(u_id, channel_id):
        raise InputError(description = 'User is already an owner of the channel.')
            
    # Check the token is valid and the user calling this function is authorized.
    calling_user = data.session_search('token', token)
    if calling_user == None:
        raise AccessError(description = 'Invalid token.')
    global_owner = data.account_search('u_id', calling_user['u_id'])['is_global_owner']
    channel_owner = data.is_owner(calling_user['u_id'], channel_id)
    if not (global_owner or channel_owner):
        raise AccessError(description = 'User not authorized.')
        
    # All checks passed. Add/promote user with u_id u_id as necessary.
    promoted_member = data.make_member(u_id)
    if data.is_member(u_id, channel_id):
        data.promote_owner(channel_id, promoted_member)
    else:
        data.add_member(channel_id, promoted_member)
        data.promote_owner(channel_id, promoted_member)
        
    return {
    }

def channel_removeowner(token, channel_id, u_id):
    
    '''
    Remove the user with u_id u_id as an owner of the channel with channel_id
    channel_id.
    
    Args:
        token (str): token of user attempting to remove a user as an owner.
        channel_id (int): channel_id of the channel a user is to be removed
        as an owner from.
        u_id (int): u_id of the user who is to be removed as an owner.
        
    Return:
        {}
        
    Raises:
        AccessError: If the token does not belong to a user who is either an
        owner of the channel with channel_id channel_id or a global owner
        of Flockr.
        InputError: The channel with channel_id channel_id doesn't exist,
        the user with u_id u_id is not an owner of the channel with
        channel_id channel_id or the user with token token is attempting to
        remove themselves as an owner.
    '''

    # First get the channel if it exists.
    channel = data.channels_search('channel_id', channel_id)
    if channel == {}:
        raise InputError(description = 'Channel does not exist.')
    
    # Check that the user with u_id is already an owner of the channel.
    if not data.is_owner(u_id, channel_id):
        raise InputError(description = 'User is not an owner of the channel.')
            
    # Check the token is valid and the user calling this function is authorized.
    calling_user = data.session_search('token', token)
    if calling_user == None:
        raise AccessError(description = 'Invalid token.')
    global_owner = data.account_search('u_id', calling_user['u_id'])['is_global_owner']
    channel_owner = data.is_owner(calling_user['u_id'], channel_id)
    if not (global_owner or channel_owner):
        raise AccessError(description = 'User not authorized.')
        
    # Check that the user calling the function is not trying to remove themselves.
    if calling_user['u_id'] == u_id:
        raise InputError(description = 'User cannot remove themselves as owner.')
        
    # All checks passed. Demote user with u_id u_id as necessary.
    data.remove_ownership(channel_id, u_id)

    return {
    }
