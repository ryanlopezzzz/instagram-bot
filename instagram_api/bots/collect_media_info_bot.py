"""
Collects media (post) info from users we've collected user info on.
"""
from instagram_private_api import (ClientError, ClientConnectionError)
import time
import numpy as np
import pandas as pd
import os
import sys
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils.safe_api import (SafeClientExtended, RequestingBadInfoException)
from utils.save_api_data_helpers import (add_user_feed_to_csv, user_id_in_table)

def should_collect_media_info_on_user(user_id, user_table, media_table):
    """
    Should only collect media data on novel, public accounts with posts
    """
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
api = SafeClientExtended(api_username, retry_failed_call=True, max_api_calls_per_hour=160, 
                api_call_wait_time_generator = lambda : np.random.uniform(low=10.0, high=20.0))
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

#previous users which have given client errors.
bad_user_ids = [51182897960, 13053481207, 1295208947, 4350769776, 44299115548, 44753617779, 
                32788714015, 12364239772, 50750437882, 6230984983, 5872393888, 1811694664, 13096914, 
                1077448382, 49823679205, 50820893565, 50740850513, 46272456547, 48843118405, 27396305200, 
                1707557882, 7388340598]

#Run data collecting bot
client_errors = 0
for user_id in loaded_user_table.index.values:
    if should_collect_media_info_on_user(user_id, loaded_user_table, loaded_media_table):
        if user_id in bad_user_ids:
            continue
        print(f'Collecting media data on user id {user_id}')
        try:
            _ = add_user_feed_to_csv(api, user_id, media_table_filename, num_results_stop_api_at = 100)
        except RequestingBadInfoException as e:
            print('Exception: %s, Message: %s'%(type(e).__name__,e))
        except ClientConnectionError as e:
            print('Exception: %s, Message: %s'%(type(e).__name__,e))
        except ClientError as e:
            print('Exception: %s, Message: %s'%(type(e).__name__,e))
            client_errors+=1
            if client_errors == 3:
                print('Too many client errors')
                break
            time.sleep(60)
print('Completed data collection for current user table')
