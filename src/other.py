import data
from error import AccessError, InputError
from standup import standup_cancel_timers

def clear():
    '''
    Resets the internal data of the application to it's initial state.
    Args: none
    Return: {}
    '''

    data.u_id_stat = 0
    data.channel_id_stat = 0
    data.message_id_stat = 0
    data.users.clear()
    data.sessions.clear()
    data.channels.clear()
    data.reset_list.clear()
    data.standups.clear()
    standup_cancel_timers()

    return {
    }

def users_all(token):
    '''
    Returns a list of all users and their associated details.

    Args:
        token: token of the user obtaining a list of all users.

    Return:
        { users }
        
    Raises:
        AccessError: The given token is invalid. 
    '''

    # checks for invalid token
    if not data.session_search('token', token):
        raise AccessError(description='Invalid token.')
    
    return {
        'users': data.users_info()
    }

def admin_userpermission_change(token, u_id, permission_id):
    '''
    Given a user by their user id, set their permissions to new permissions
    described by permission_id.

    Args:
        token: the token of the user changing permissions.
        u_id: the u_id of the user whose permissions will be changed.
        permission_id: the new permission_id of user with u_id 
        (permission id 1 - owner, permission id 2 - members).

    Return:
        {}

    Raises:
        AccessError: The user referred to by the token is not an owner of Flockr.
        InputError: The user with given u_id does not exist or the permission_id 
        is not a valid permission id (1 or 2).
    '''

    # checks for invalid token
    session = data.session_search('token', token)
    if not session:
        raise AccessError(description='Invalid token.')
    
    # checks for invalid user
    if not data.account_search('u_id', u_id):
        raise InputError(description='Invalid user id.')

    # checks for invalid permission
    if permission_id not in [1, 2]:
        raise InputError(description='Invalid permission id.')

    # checks that inviter is a global owner
    inviter_u_id = session['u_id']
    if not data.is_global_owner(inviter_u_id):
        raise AccessError(description='User is not a global owner.')

    # no effect if global owner tries to change their own permissions
    if inviter_u_id == u_id:
        return {
        }

    # sets new permission of the user
    data.set_global_permissions(u_id, permission_id)    

    return {
    }

def search(token, query_str):

    '''
    Search for a message containing query_str in all the channels the user
    with token token has joined.
    
    Args:
        token (str): token of calling user.
        query_str (str): Search for messages containing this string.
        
    Return:
        result (list): List of messages containing the query string.
        
    Raises:
        AccessError: No user with token token.
    '''

    # Get the user.
    calling_session = data.session_search('token', token)
    if calling_session == None:
        raise AccessError(description = 'Invalid Token')
    calling_u_id = calling_session['u_id']

    # Search logic.
    result = {
        'messages': [], 
    }
    user_channels = data.channels_search('all_members', calling_u_id)
    for channel in user_channels:
        for message in channel['messages']:
            if query_str in message['message']:
                result['messages'].append(message)
    result['messages'] = sorted(result['messages'], key = lambda i: i['message_id'])
   
    return result
