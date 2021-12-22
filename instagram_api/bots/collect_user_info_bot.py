"""
Collects user info of followers of random users.
"""
import numpy as np
import os
import sys
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils.api_requests import (UserInfo, get_random_username)
from utils.safe_api import SafeClient
from utils.save_api_data_helpers import add_followers_user_info_to_csv

api_username = 'cuteanimalzzzz123'
api_password = 'instabotOP'
api = SafeClient(api_username, api_password, retry_failed_call=True, max_api_calls_per_hour=160, 
                api_call_wait_time_generator = lambda : np.random.uniform(low=4.0, high=8.0))
print('Logged in to user %s'%api_username)
user_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_user_info_table.csv'%api_username)
while True:
    random_username = get_random_username(api)
    random_user_info= UserInfo(api, random_username)
    if random_user_info.follower_count > int(1e2) or random_user_info.private_status is True: #Random user is too popular to collect all followers info 
        print('Found %s with %d follower_count and private_status '%(random_username, random_user_info.follower_count) + str(random_user_info.private_status))
        continue
    print()
    print('Collecting info on %s\'s %d followers'%(random_username, random_user_info.follower_count))
    add_followers_user_info_to_csv(api, random_username, user_table_filename)
    print('Finished collecting info on %s'%random_username)
    print()