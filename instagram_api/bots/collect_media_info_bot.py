"""
Collects media (post) info from users we've collected user info on.
"""
import numpy as np
import pandas as pd
import os
import sys
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils.safe_api import (SafeClientExtended, RequestingBadInfoException)
from utils.save_api_data_helpers import (add_user_feed_to_csv, user_id_in_table)

def should_collect_media_info_on_user(user_id, user_table, media_table):
    if user_id_in_table(user_id, media_table) == True:
        return False
    elif user_table.loc[user_id].private_status == True:
        return False
    elif user_table.loc[user_id].media_count == 0:
        return False
    else:
        return True

#Log In
api_username = 'cuteanimalzzzz123'
api_password = 'instabotOP'
api = SafeClientExtended(api_username, api_password, retry_failed_call=True, max_api_calls_per_hour=160, 
                api_call_wait_time_generator = lambda : np.random.uniform(low=8.0, high=16.0))
print('Logged in to user %s'%api_username)

#Load user info table
user_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_user_info_table.csv'%api_username)
if os.path.isfile(user_table_filename):
    loaded_user_table = pd.read_csv(user_table_filename, index_col=0)
else:
    raise ValueError('Must have user table to load')

#Load media info table
media_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_media_info_table.csv'%api_username)
if os.path.isfile(media_table_filename):
    loaded_media_table = pd.read_csv(media_table_filename, index_col=0)
else:
    loaded_media_table = None

#Run data collecting bot
for user_id in loaded_user_table.index.values:
    if should_collect_media_info_on_user(user_id, loaded_user_table, loaded_media_table):
        print(f'Collecting media data on user id {user_id}')
        try:
            _ = add_user_feed_to_csv(api, user_id, media_table_filename, num_results_stop_api_at = 100)
        except RequestingBadInfoException as e:
            print('Exception: %s, Message: %s'%(type(e).__name__,e))
print('Completed data collection for current user table')
