######################## TEST FOR auth.py ############################
import auth
from other import clear
import pytest
from error import AccessError, InputError

@pytest.fixture
def input_register():
    '''
    makeup input for testing auth_register
    '''

    return (
        # email is used
        ['jackbrian@gmail.com', 'hf85H4t8Fuhr', "Jack", 'Brian'],
        # invalid email format
        ['jackbrian', 'hf85H4t8Fuhr', 'Jack', 'Brian'],
        # password too short
        ['petermiller@outlook.com', '123', 'Peter', 'Miller'],
        # first name too long
        ['petermiller@outlook.com', 'hf85H4t8Fuhr', 'PPPPPPPPPPPPPeeeeeeeeeeeeettttttttttttteeeeeeeeeeeeerrrrrrrrrrrrrr', 'Miller'],
        # last name too long
        ['petermiller@outlook.com', 'hf85H4t8Fuhr', 'Peter', 'MMMMMMMMMMMiiiiiiiiiiillllllllllllllllllllllleeeeeeeeeeeeeerrrrrrrrrr']
    )

@pytest.fixture
def input_login():
    '''
    makeup input for testing auth_login
    '''

    return (
        # invalid email format
        ('jackbrian', 'hf85H4t8Fuhr'),
        # email not found
        ('petermiller@outlook.com', 'hf85H4t8Fuhr'),
        # wrong password
        ('jackbrian@gmail.com', '1234567'),
    )

#--------------------------------------TEST FOR auth_register-------------------------------------
def test_auth_register():
    '''
    successful registration
    '''
    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    clear()

def test_auth_register_InputError(input_register):
    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    for i in range(5):
        with pytest.raises(InputError):
            auth.auth_register(input_register[i][0], input_register[i][1], input_register[i][2], input_register[i][3])
    clear()
        
#----------------------------------------TEST FOR auth_login------------------------------------------
def test_auth_login():
    '''
    successful login
    '''

    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    assert(auth.auth_login('jackbrian@gmail.com', 'hf85H4t8Fuhr'))
    clear()

def test_auth_login_InputError(input_login):
    '''
    unsuccessful login
    '''

    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    for i in range(3):
        with pytest.raises(InputError):
            auth.auth_login(input_login[i][0], input_login[i][1])
    clear()

#----------------------------------------TEST FOR auth_logout------------------------------------------
def test_auth_logout():
    '''
    successful logout
    '''

    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    token = auth.auth_login('jackbrian@gmail.com', 'hf85H4t8Fuhr')['token']
    assert(auth.auth_logout(token))
    clear()

def test_auth_logout_fail():
    '''
    unsuccessful logout
    '''
    
    auth.auth_register('jackbrian@gmail.com', 'hf85H4t8Fuhr', 'Jack', 'Brian')
    with pytest.raises(AccessError):
        auth.auth_logout("fuwegfiweh")
    clear()
