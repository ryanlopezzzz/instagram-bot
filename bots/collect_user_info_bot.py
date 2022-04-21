"""
Collects user info of followers of random users.
"""
import numpy as np
import pandas as pd
import os
import sys
import names
import random
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils.safe_api import SafeClientExtended
from utils.save_api_data_helpers import (add_followers_user_info_to_csv, user_id_in_table)

def get_new_random_public_user_id(api, user_table):
    """
    Returns a psuedo-random user_id that is public, not already in the user_table, and has less than 10,000 followers
    (since API has encountered error with very popular users).
    """
    while True:
        random_first_name = names.get_first_name()
        search_results = api.search_users(random_first_name)['users']
        public_user_ids = [user['pk'] for user in search_results if user['is_private'] == False]
        new_public_user_ids = [user_id for user_id in public_user_ids if user_id_in_table(user_id,user_table) == False]
        num_results = len(new_public_user_ids)
        if num_results == 0:
            continue
        return_result_index = random.randint(0, num_results-1)
        random_user_id = new_public_user_ids[return_result_index]
        if api.user_info(random_user_id)['follower_count'] >= 1e4:
            continue
        else:
            break
    return random_user_id

#Log In
api_username = 'cuteanimalzzzz123'
api_password = 'instabotOP'
api = SafeClientExtended(api_username, api_password, retry_failed_call=True, max_api_calls_per_hour=160, 
                api_call_wait_time_generator = lambda : np.random.uniform(low=4.0, high=8.0))
print('Logged in to user %s'%api_username)

#Collect data infinitely
while True:
    #Load user info table
    user_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_user_info_table.csv'%api_username)
    if os.path.isfile(user_table_filename):
        loaded_user_table = pd.read_csv(user_table_filename, index_col=0)
    else:
        loaded_user_table = None

    #Collect follower on random user id
    random_user_id = get_new_random_public_user_id(api, loaded_user_table)
    print(f'Collecting data on random user id {random_user_id}')
    add_followers_user_info_to_csv(api, random_user_id, user_table_filename, num_results_stop_api_at = 1e3)
    print('Finished collecting info on %s'%random_user_id)
    print()