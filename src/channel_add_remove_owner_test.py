import auth
import channel
import channels
from error import AccessError, InputError
import other
import pytest

# ADDOWNER AND REMOVEOWNER TESTS ============================
@pytest.fixture
def add_remove_fixture():
    '''
    A fixture that creates 4 users (3 non global owner users) and
    u1 also creates a channel. 4 users and c_id are returned.
    '''
    other.clear()
    u_global = auth.auth_register('eG@email.com', 'passwordG', 'firstG', 'lastG')
    u1 = auth.auth_register('e1@email.com', 'password1', 'first1', 'last1')
    u2 = auth.auth_register('e2@email.com', 'password2', 'first2', 'last2')
    u3 = auth.auth_register('e3@email.com', 'password3', 'first3', 'last3')
    c_id = channels.channels_create(u1['token'], 'channel1', True)['channel_id']
    return (u_global, u1, u2, u3, c_id)

def test_channel_addowner_global_owner(add_remove_fixture):
    '''
    Tests that a global owner can add anyone to any channel as an owner.
    '''
    (u_global, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u_global['token'], c_id, u2['u_id'])
    c_owners = channel.channel_details(u1['token'], c_id)['owner_members']
    assert(any(u2['u_id'] == owner['u_id'] for owner in c_owners))

def test_channel_addowner_two_users(add_remove_fixture):
    '''
    Tests that the owner of a channel (u1) can add another user (u2) as an 
    owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    c_owners = channel.channel_details(u1['token'], c_id)['owner_members']
    assert(any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    
def test_channel_addowner_three_users(add_remove_fixture):
    '''
    Tests that owner permissions correctly apply to u2 after the prior test
    case by testing that u2 can now add u3 as an owner of the channel.
    '''
    (_, u1, u2, u3, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    channel.channel_addowner(u2['token'], c_id, u3['u_id'])
    c_owners = channel.channel_details(u1['token'], c_id)['owner_members']
    assert(any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u3['u_id'] == owner['u_id'] for owner in c_owners))
    
def test_channel_addowner_invalid_channel_id(add_remove_fixture):
    '''
    Tests that an InputError is raised when an invalid channel_id is provided.
    '''
    (_, u1, u2, _, _) = add_remove_fixture
    with pytest.raises(InputError):
        channel.channel_addowner(u1['token'], -42, u2['u_id'])

def test_channel_addowner_add_self(add_remove_fixture):
    '''
    Tests that an InputError is raised if an owner attempts to add themselves
    as an owner of the channel they are already an owner of.
    '''
    (_, u1, _, _, c_id) = add_remove_fixture
    with pytest.raises(InputError):
        channel.channel_addowner(u1['token'], c_id, u1['u_id'])
    
def test_channel_addowner_add_within(add_remove_fixture):
    '''
    Tests that an InputError is raised if another owner tries to add a user who 
    is already an owner of a channel as an owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    with pytest.raises(InputError):
        channel.channel_addowner(u2['token'], c_id, u1['u_id'])
        
def test_channel_addowner_add_unauthorized(add_remove_fixture):
    '''
    Tests that an AccessError is raised if a member but not an owner of a
    channel tries to add another non-owner user as an owner.
    '''
    (_, _, u2, u3, c_id) = add_remove_fixture
    channel.channel_join(u2['token'], c_id)
    with pytest.raises(AccessError):
        channel.channel_addowner(u2['token'], c_id, u3['u_id'])
    
def test_channel_addowner_already_joined(add_remove_fixture):
    '''
    Tests that a member can be correctly added as an owner of a channel by
    an authorized user.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_join(u2['token'], c_id)
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    c_owners = channel.channel_details(u1['token'], c_id)['owner_members']
    assert(any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    
def test_channel_addowner_invalid_token(add_remove_fixture):
    '''
    Tests that an AccessError is raised if an invalid token is given.
    '''
    (_, _, u2, _, c_id) = (add_remove_fixture)
    with pytest.raises(AccessError):
        channel.channel_addowner('NotAToken', c_id, u2['u_id'])

def test_channel_removeowner_global_owner(add_remove_fixture):
    '''
    Tests that a global owner can remove anyone as an owner from any channel.
    '''
    (u_global, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    channel.channel_removeowner(u_global['token'], c_id, u2['u_id'])
    c_details = channel.channel_details(u1['token'], c_id)
    c_owners = c_details['owner_members']
    c_members = c_details['all_members']
    assert(not any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u2['u_id'] == member['u_id'] for member in c_members))

def test_channel_removeowner_new_owner(add_remove_fixture):
    '''
    Tests that an owner can correctly remove a user as an owner of a channel
    after adding them as an owner.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    channel.channel_removeowner(u1['token'], c_id, u2['u_id'])
    c_details = channel.channel_details(u1['token'], c_id)
    c_owners = c_details['owner_members']
    c_members = c_details['all_members']
    assert(not any(u2['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u2['u_id'] == member['u_id'] for member in c_members))
    
def test_channel_removeowner_original_creator(add_remove_fixture):
    '''
    Tests that a newly added owner of a channel can remove the user who made
    them an owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    channel.channel_removeowner(u2['token'], c_id, u1['u_id'])
    c_details = channel.channel_details(u1['token'], c_id)
    c_owners = c_details['owner_members']
    c_members = c_details['all_members']
    assert(not any(u1['u_id'] == owner['u_id'] for owner in c_owners))
    assert(any(u1['u_id'] == member['u_id'] for member in c_members))

def test_channel_remove_owner_bad_channel_id(add_remove_fixture):
    '''
    Tests that an InputError is raised if an invalid channel_id is provided.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    with pytest.raises(InputError):
        channel.channel_removeowner(u1['token'], -42, u2['u_id'])
    
def test_channel_removeowner_non_member(add_remove_fixture):
    '''
    Tests that an InputError is raised if the user being removed as an owner
    isn't a member or owner of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    with pytest.raises(InputError):
        channel.channel_removeowner(u1['token'], c_id, u2['u_id'])
        
def test_channel_removeowner_self_removal(add_remove_fixture):
    '''
    Tests that an InputError is raised when an owner attempts to remove
    themselves as an owner.
    '''
    (_, u1, _, _, c_id) = add_remove_fixture
    with pytest.raises(InputError):
        channel.channel_removeowner(u1['token'], c_id, u1['u_id'])
    
def test_channel_removeowner_non_owner(add_remove_fixture):
    '''
    Tests that an InputError is raised if the user being removed as an owner
    isn't an owner of the channel but is a member of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_join(u2['token'], c_id)
    with pytest.raises(InputError):
        channel.channel_removeowner(u1['token'], c_id, u2['u_id'])
    
def test_channel_removeowner_unauthorized(add_remove_fixture):
    '''
    Tests that an AccessError is raised if the user calling the function isn't 
    an owner of the channel but is a member of the channel.
    '''
    (_, u1, u2, _, c_id) = add_remove_fixture
    channel.channel_join(u2['token'], c_id)
    with pytest.raises(AccessError):
        channel.channel_removeowner(u2['token'], c_id, u1['u_id'])
        
def test_channel_removeowner_invalid_token(add_remove_fixture):
    '''
    Tests that an AccessError is raised if an invalid token is provided.
    '''
    (_, u1, u2, _, c_id) = (add_remove_fixture)
    channel.channel_addowner(u1['token'], c_id, u2['u_id'])
    with pytest.raises(AccessError):
        channel.channel_removeowner('NotAToken', c_id, u2['u_id'])
