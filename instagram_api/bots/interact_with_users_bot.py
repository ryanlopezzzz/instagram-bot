import os
import sys
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils.safe_api import SafeClient
from utils.interaction_metric import rank_for_interactions
from utils.api_requests import (PublicUserInfoRequests, InteractWithUsersActions)
import numpy as np
import pandas as pd
import requests
import random
import time

def get_random_comment():
        comment_components = [
            ['hello ', 'hey ', 'hi '],
            ['I just started '],
            ['a ', 'my '],
            ['new '],
            ['account', 'profile', 'instagram'],
            ['! '],
            ['I '],
            ['will be ', 'plan to be ', 'am going to be '],
            ['posting a nice picture and inspirational quote everyday like this: \"'],
            [random.choice(requests.get('https://type.fit/api/quotes').json())['text']],
            ['\" I would love if you checked my page out!']
        ]
        random_comment = ''
        for component in comment_components:
            random_comment += random.choice(component)
        return random_comment

#Log into account used for interactions
api_username = 'ds_club_2021'
api_password = 'instabotOP'
max_likes_per_hour = max_comments_per_hour = 20
api = SafeClient(api_username, api_password, retry_failed_call=True, max_api_calls_per_hour=max_likes_per_hour+max_comments_per_hour, 
                api_call_wait_time_generator = lambda : np.random.uniform(low=25.0, high=50.0))
print('Logged in')

while True:
    #Load table of user info
    table_username = 'cuteanimalzzzz123'
    user_table_filename = os.path.join(instagram_api_folder,'saved_info/%s_collected_user_info_table.csv'%table_username)
    if os.path.isfile(user_table_filename):
        loaded_user_table = pd.read_csv(user_table_filename)
        loaded_user_table.set_index('user_id', inplace=True)
    else:
        loaded_user_table = None
    print('Loaded user table')

    #Load interaction table for api user
    interaction_columns = ['media_id', 'user_id', 'media_liked', 'comment_left', 'api_request_time']
    interaction_table_filename = os.path.join(instagram_api_folder,'saved_info/%s_interacted_with_table.csv'%api_username)
    if os.path.isfile(interaction_table_filename):
        loaded_interaction_table = pd.read_csv(interaction_table_filename)
    else:
        loaded_interaction_table = pd.DataFrame(columns = interaction_columns)
    loaded_interaction_table.set_index('media_id', inplace=True)
    print('Loaded interaction table')

    #Get user_id with max interaction metric and not already interacted with
    ranked_table = rank_for_interactions(loaded_user_table)
    users_interacted_with = ranked_table.index.isin(loaded_interaction_table['user_id'])
    ranked_table = ranked_table[~users_interacted_with]
    max_interaction_user_id = ranked_table['interaction_score'].idxmax()
    max_interaction_username = ranked_table.loc[max_interaction_user_id]['username']
    print('Got username to interact with %s'%max_interaction_username)

    #Like users first post and make random comment
    first_media = api.user_feed(max_interaction_user_id)['items'][0]
    first_media_id = first_media['id']

    iwua = InteractWithUsersActions(api)
    api_request_time = time.time()
    iwua.like_post(first_media_id)
    print('Liked Post')

    commenting_disabled_key = 'commenting_disabled_for_viewer'
    if commenting_disabled_key not in first_media.keys(): #comments are enabled
        random_comment = get_random_comment()
        iwua.post_comment(first_media_id, random_comment)
        print('Commented on a post')
    elif first_media[commenting_disabled_key] == True: #comments disabled
        print('Commenting on post is disabled')
        random_comment = ''
    else:
        print('This should not occur, I think.')
    new_row = pd.DataFrame([[first_media_id, max_interaction_user_id, True, random_comment, api_request_time]], columns=interaction_columns)
    new_row.set_index('media_id', inplace=True)
    new_interaction_table = pd.concat([loaded_interaction_table, new_row])
    new_interaction_table.to_csv(interaction_table_filename)
    print('Updated interaction table')


