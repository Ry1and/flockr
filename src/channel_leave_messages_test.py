####TESTS FOR CHANNEL####
import pytest
import channel
import channels
import auth
import error
import other



##### TESTS FOR CHANNEL_LEAVE #####
@pytest.fixture
def leave_fixture():
    other.clear()
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    user1 = auth.auth_register('name1@gmail.com', 'password1', 'f_name1', 'l_name1')
    user2 = auth.auth_register('name2@gmail.com', 'password2', 'f_name2', 'l_name2')

    channel_id = channels.channels_create(user0['token'], "generic channel", True)['channel_id']

    return (user0, user1, user2,channel_id)


#channel leave when user is a member
def test_leave_one_member(leave_fixture):
    
    (user0, user1, _, channel_id) = leave_fixture
    
    #add user1 to 'generic channel' as a member
    channel.channel_invite(user0['token'], channel_id, user1['u_id'])
 

    #leave the channel as user1
    channel.channel_leave(user1['token'], channel_id)
    
    #check if user 1 is still in the channel as a member
    details = channel.channel_details(user0['token'],channel_id)

    has_left = True
    for member in details['all_members']:
        if member['u_id'] == user1['u_id']:
            has_left = False

    assert(has_left == True)


def test_leave_two_member(leave_fixture):
    (user0, user1, user2, channel_id) = leave_fixture
    
    #user0 adds user1 and user2 to 'generic channel'
    channel.channel_invite(user0['token'], channel_id, user1['u_id'])
    channel.channel_invite(user0['token'], channel_id, user2['u_id'])

    # user1 and user2 leave 'generic channel'
    channel.channel_leave(user1['token'],channel_id)
    channel.channel_leave(user2['token'],channel_id)

   # check if user1 and user2 have left generic channel
    details = channel.channel_details(user0['token'],channel_id)


    user1_left = True
    user2_left = True
    for member in details['all_members']:
        if member['u_id'] == user1['u_id']:
            user1_left = False
    
    for member in details['all_members']:
        if member['u_id'] == user2['u_id']:
            user2_left = False

    assert(user1_left == True and user2_left == True)

#leaving a channel as an owner (but not the last owner)

def test_leave_owner(leave_fixture):
    (user0, user1, _, channel_id) = leave_fixture

    #add user1 as an owner of 'generic channel'
    channel.channel_addowner(user0['token'], channel_id, user1['u_id'])

    #user1 leaves the channel
    channel.channel_leave(user1['token'], channel_id)

    #ensure user1 is not an owner or member of generic channel
    details = channel.channel_details(user0['token'],channel_id)

    u1_owner_left = True
    for member in details['owner_members']:
        if member['u_id'] == user1['u_id']:
            u1_owner_left = False

    u1_member_left = True
    for member in details['all_members']:
        if member['u_id'] == user1['u_id']:
            u1_member_left = False

    assert(u1_member_left == True and u1_owner_left == True)
            

# leaving a channel as the last owner
# channel should be deleted
def test_leave_last_owner(leave_fixture):
    (user0, _, _, channel_id) = leave_fixture

    channel.channel_leave(user0['token'], channel_id)

    
    all_channels = channels.channels_listall(user0['token'])['channels']

    channel_exists = False

    for c in all_channels:
        if c['channel_id'] == channel_id:
            channel_exists = True

    assert(channel_exists == False)


#when user tries to leave a channel that they arent in
def test_leave_not_member(leave_fixture):
    (_, user1, _, channel_id) = leave_fixture
    
    with pytest.raises(error.AccessError):
        channel.channel_leave(user1['token'],channel_id)


# when user tries to leave a channel that doesnt exist
def test_leave_no_channel(leave_fixture):
    (_, user1, _, _) = leave_fixture
    
    with pytest.raises(error.InputError):
        #user1 tries to leave channel with channel_id '213', which doesnt exist
        channel.channel_leave(user1['token'],213)

##### END OF TESTS FOR CHANNEL_LEAVE #####


##### TESTS FOR CHANNEL_MESSAGES #####
def initialise_messages():
    other.clear()
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    user1 = auth.auth_register('name1@gmail.com', 'password1', 'f_name1', 'l_name1')
    
    #user0 creates a new channel with channel_id = 123
    channel_id = channels.channels_create(user0['token'],"generic channel",True)['channel_id']

    return user0,user1, channel_id


def test_messages_basic():
    #test if the channel_message function returns the correct info
    # when only empty messages list is in the channel
    user0, _, channel_id = initialise_messages()
    
    result = channel.channel_messages(user0['token'], channel_id, 0)['messages']
    
    assert(result == [])

    
def test_messages_valid_channel():
    # raise an InputError if an invalid channel_id is raised
    other.clear()
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    
    with pytest.raises(error.InputError):
        channel.channel_messages(user0['token'], -42,0)

def test_messages_valid_start():
    # raise an InputError if the start value provided
    # is greater than the total number of messages in the channel
    other.clear()
    user0 = auth.auth_register('name0@gmail.com', 'password0', 'f_name0', 'l_name0')
    channel_id = 123
    channel_id = channels.channels_create(user0['token'], "generic channel", True)['channel_id']
    

    
    with pytest.raises(error.InputError):
        channel.channel_messages(user0['token'],channel_id ,1000)

def test_messages_not_member():
    # raise an accesserror when a user tries to access messages 
    # in a channel where they are not a member
    _, user1, channel_id = initialise_messages()

    with pytest.raises(error.AccessError):
        channel.channel_messages(user1['token'], channel_id, 0)
