DATA_COLLECTION = {
    "auth_register": (
        {
            "email": "name1@gmail.com",
            "password": "password1",
            "name_first": "name_first1",
            "name_last": "name_last1"
        },
        {
            "email": "name2@gmail.com",
            "password": "password2",
            "name_first": "name_first2",
            "name_last": "name_last2"
        },
        {
            "email": "name3@gmail.com",
            "password": "password3",
            "name_first": "name_first3",
            "name_last": "name_last3"
        },
    ),
    "auth_register_fail":(
        {
            "email": "name1@gmail.com",
            "password": "password1",
            "name_first": "name_first1",
            "name_last": "name_last1"
        },
        {
            "email": "name2",
            "password": "password1",
            "name_first": "name_first2",
            "name_last": "name_last2"
        },
        {
            "email": "name3@gmail.com",
            "password": "123",
            "name_first": "name_first3",
            "name_last": "name_last3"
        },
        {
            "email": "name4@gmail.com",
            "password": "password4",
            "name_first": "name_first_too_long_name_too_long_name_too_long_name_too_long",
            "name_last": "name_last3"
        },
        {
            "email": "name5@gmail.com",
            "password": "password5",
            "name_first": "name_first5",
            "name_last": "name_last_too_long_name_too_long_name_too_long_name_too_long"
        }
    ),
    "auth_login": (
        {
            "email": "name1@gmail.com",
            "password": "password1"
        },
        {
            "email": "name2@gmail.com",
            "password": "password2"
        },
        {
            "email": "name3@gmail.com",
            "password": "password3"
        }
    ),
    "auth_login_fail": (
        {
            "email": "name1",
            "password": "password1"
        },
        {
            "email": "name2@gmail.com",
            "password": "password2"
        },
        {
            "email": "name1@gmail.com",
            "password": "wrong_password"
        }
    )
}