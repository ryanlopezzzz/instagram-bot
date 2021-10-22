from instagram_private_api import Client, ClientCompatPatch
import api_requests
import importlib
importlib.reload(api_requests)
from api_requests import BasicUserInfo
from api_requests import PublicUserInfoRequests
from api_requests import MediaInfoRequests

username = 'cuteanimalzzzz123'
password = 'instabotOP'
api = Client(username, password)

test_usernames = ['ryanlopezzzz', 'xu.bryana']

def test_basic_user_info(username):
    """
    Can check against true values by going onto Instagram app.
    """
    basic_user_info = BasicUserInfo(api, username)
    print("User Id: " + str(basic_user_info.user_id))
    print("Follow count: " + str(basic_user_info.follower_count))
    print("Following count: " + str(basic_user_info.following_count))
    print("Media count: " + str(basic_user_info.media_count))
    print("Private status: " + str(basic_user_info.private_status))

for username in test_usernames + large_test_usernames:
    print("Username: " + username)
    test_basic_user_info(username)
    print("-"*100)