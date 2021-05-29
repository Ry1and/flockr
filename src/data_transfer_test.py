import other
import auth
import data
import json

def test_data_transfer():
    '''
    successful transfer of data from memory to databse file
    '''

    data.load("src/database.json")
    auth.auth_register('user1@gmail.com', 'password1', 'name_1', 'surname_1')
    data.save("src/database.json")
    with open("src/database.json", 'r') as FILE:   
        database = json.load(FILE)
        assert database == {"u_id_stat": 1, 
            "channel_id_stat": 0, 
            "message_id_stat": 0, 
            "users": [
                {
                    'u_id': 1,
                    'email': 'user1@gmail.com',
                    'name_first': 'name_1',
                    'name_last': 'surname_1',
                    'password': '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e',
                    'handle_str': 'name_1surname_1',
                    'is_global_owner': True,
                }
            ],
            "sessions": [
                {
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxfQ.v_my_TX_rAVtWZLx1lMuG4v5xNDNdu-2f7jYZDA9YU8",
                    "u_id": 1
                }
            ],
            "channels": [],
            "reset_list": []
        }
    other.clear()
    data.save("src/database.json")
    with open("src/database.json", 'r') as FILE:   
        database = json.load(FILE)
        assert database == {"u_id_stat": 0, 
            "channel_id_stat": 0, 
            "message_id_stat": 0, 
            "users": [],
            "sessions": [],
            "channels": [],
            "reset_list": []
        }
