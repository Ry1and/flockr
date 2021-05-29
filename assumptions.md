================================================================================
GENERAL:
-All times are UTC.

================================================================================
AUTH:

Registration == Login as a new user
The difference between registration and login is that registration is for new 
users and login is for old/existing users, whereas both operations log this account 
in if information provided is valid, new session will be created in both cases 
and unique tokens will be generated and returned.

Repeated login from same account:
When a new login request is raised from an account that is already logged in or 
registered and hasn't logged out, by default we will re-log this account in and 
assign a new active token, the last token will therefore be de-activated as its 
session no longer exists.

Generated token and u_id:
For now, token will be generated such that it's a string consist of random 6 
digits, u_id will be your place in the whole user database, eg. if you are the 
6th registered user, your u_id will be 6. Everytime a new token is generated, a 
check will take place so that this new token doesn't repeat with any existing token.

Return value of logout:
If token is valid, and session is successfully deleted, return {'is_success': True}, 
if token is valid but session is not deleted, return {'is_success': False}, if token 
is invalid, AccessError is raised.

================================================================================
CHANNEL:

Channel deletion:
A channel is deleted when the last member has left or been removed from the channel.
When the last owner of the channel has left or been removed, if there are remaining 
members, the first member that joined the channel will be promoted as owner. 

Channel permissions:
An owner of the channel can remove any member or owner from the group and promote any 
member to owner. An owner can demote any owner to member, except themselves. 
The global owner of flockr can join any existing channel, and can change the 
permissions of all members in a channel regardless of whether they are within the 
channel, e.g. the global owner can promote a member of a channel, or demote an owner 
of the channel. Once a global owner joins or is invited to a channel, they will 
be promoted as an owner of the channel. 

Inviting or joining within a channel: 
Inviting a member or owner to a channel they are already in will have no effect.
Joining a channel that a member or owner is in will have no effect. 

Channel Addowner:
A person who is added as an owner to a channel via channel_addowner joins the 
channel if they are not a member of the channel automatically.

Channel Removeowner:
People who are removed as owners of a channel via channel_removeowner stay
in the channel as members.

Channel Messages:
If there are no messages in channel_messages will return an empty list.
All new messages are inserted at the beginning of the messages list.

Misc testing Assumptions:
-42 is never a valid channel_id.

================================================================================
CHANNELS:

channels_list and channels_listall will return {'channels':[]} if there are no channels 
to be returned. channels_create will make the user associated with the token the owner
of the channel.

================================================================================
USER:

Global permissions:
The global owner can promote or demote any member to global owner. The global 
owner cannot demote themselves to a member. 

Repeat yourself:
When user tries to reset some of his/her profile, if the info provided is exactly the 
same as already existed in his/profile, nothing will be done.

Uploading profile photo:
The profile_img_url does not exist unless the server is running. 
Every user starts with the same default profile photo, stored in the directory 
'src/default' as 'default_img.jpg' when the server is run. 
An img_url that is invalid will raise an InputError. 
Any img_url given that cannot be opened by urllib.request.urlretrieve will raise
an InputError. 

Cropping an image:
Negative dimensions given (i.e. any of x_start, y_start, x_end, y_end less than 
zero) are not allowed and will raise an InputError.
Length and width given must be positive, that is, x_start must be less than 
x_end and y_start must be less than y_end. 

================================================================================
MESSAGES:

Message send:
Newly sent messages do not have any reacts and are not pinned.

Message pin, Message unpin:
Error checks are done in this order.
    - Invalid token (AccessError)
    - Message does not exist (InputError)
    - Not member of channel (AccessError)
    - Not channel owner (AccessError)
    - Message already pinned/unpinned (InputError)
    
Message Edit:
    - time_created of message is not updated when message is edited.

Message Send Later:
    - If the user sends a message at a particular time in the future and
      the user leaves the channel before the message is sent, the message is still sent at the specified send time.


    
================================================================================
STANDUPS:

General:
    - Messages sent with standup_send will still be bundled into a message
      sent by the user who started the standup, even if any user logs out
      during the standup.
    - For timing of standups closing there is a small margin for error (a few
      seconds).
    - If no messages are sent to the standup, no messages are posted when the standup
      ends.
