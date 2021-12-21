"""
Helper functions for saving API collected data to pandas tables / csv files
"""
import pandas as pd
from api_requests import (UserInfo, PublicUserInfoRequests)
import time
import os

def add_followers_user_info_to_csv(api, username, user_table_filename):
    """
    Adds username's followers user info to user_table_filename csv file
    """
    followers_usernames = PublicUserInfoRequests(api, username).get_followers_usernames()
    generated_user_table = get_user_info_table(api, followers_usernames)
    if os.path.isfile(user_table_filename): #Load existing CSV file if exists
        loaded_user_table = pd.read_csv(user_table_filename)
        loaded_user_table.set_index('user_id', inplace=True)
    else:
        loaded_user_table = None
    new_user_table = combine_user_info_tables(loaded_user_table, generated_user_table)
    new_user_table.to_csv(user_table_filename)

def get_user_info_table(api, usernames):
    """
    Collects user info for each username through API and formats as pandas dataframe
    """
    column_names_for_table = ['user_id', 'username', 'private_status', 'follower_count', 'following_count', 
                              'media_count', 'full_name', 'profile_pic_url', 'bio_text', 'url_in_bio', 
                              'hashtag_following_count', 'usertags_count', 'api_request_time']
    table_rows = []
    for username in usernames:
        user_info = UserInfo(api, username)
        user_info_attributes = column_names_for_table[:-1]
        single_user_data = [user_info.__dict__[attribute] for attribute in user_info_attributes]
        api_request_time = time.time()
        row_data = single_user_data + [api_request_time]
        table_rows.append(row_data)
    dataframe = pd.DataFrame(table_rows, columns=column_names_for_table)
    dataframe.set_index('user_id', inplace=True)
    return dataframe

def combine_user_info_tables(table1, table2):
    """
    Combines tables along user_id while eliminating duplicates by only keeping the most recently collected data
    """
    #combine tables
    new_table = pd.concat([table1, table2])
    
    #sort so most recent data is on top
    new_table = new_table.sort_values('api_request_time', ascending=False)
    
    #get indices of rows with duplicated user_ids, except for their first (most recent) appearance in the table
    duplicated_indices = new_table.index.duplicated(keep='first')

    #exclude duplicated user_id rows which are not most recent
    new_table = new_table[~duplicated_indices]
    
    return new_table
