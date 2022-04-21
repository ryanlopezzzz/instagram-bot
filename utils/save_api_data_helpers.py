"""
Helper functions for saving API collected data to pandas tables / csv files
"""
import pandas as pd
import time
import os

def add_following_user_info_to_csv(api, user_id, user_table_filename, **api_kwargs):
    """
    Returns next_begin_query_id and adds user_id's followers' user info to csv file.
    """
    following_ids, next_begin_query_id = api.user_following(user_id, **api_kwargs)
    following_ids_partition = [following_ids[x:x+20] for x in range(0, len(following_ids), 20)] #save table every 20 results
    for following_ids_subset in following_ids_partition:
        user_table = get_user_info_table(api, following_ids_subset)
        update_csv_file(user_table, user_table_filename)
    return next_begin_query_id

def add_followers_user_info_to_csv(api, user_id, user_table_filename, **api_kwargs):
    """
    Returns next_begin_query_id and adds user_id's followers' user info to csv file.
    """
    followers_ids, next_begin_query_id = api.user_followers(user_id, **api_kwargs)
    followers_ids_partition = [followers_ids[x:x+20] for x in range(0, len(followers_ids), 20)] #save table every 20 results
    for followers_ids_subset in followers_ids_partition:
        user_table = get_user_info_table(api, followers_ids_subset)
        update_csv_file(user_table, user_table_filename)
    return next_begin_query_id

def add_user_feed_to_csv(api, user_id, media_table_filename, **api_kwargs):
    """
    Returns next_begin_query_id and adds user_id's media (post) info to csv file.
    """
    media_table, next_begin_query_id = get_user_feed_table(api, user_id, **api_kwargs)
    update_csv_file(media_table, media_table_filename)
    return next_begin_query_id

def get_user_info_table(api, user_ids):
    """
    Collects user info for each user_id through API and formats as pandas dataframe.
    """
    user_info_keys = ['user_id', 'username', 'private_status', 'follower_count', 'following_count', 'media_count',
                      'full_name', 'profile_pic_url', 'bio_text', 'url_in_bio', 'hashtag_following_count', 
                      'usertags_count']
    column_names_for_table = user_info_keys + ['api_request_time']
    table_rows = []
    for user_id in user_ids: #loop through different users
        single_user_info = api.user_info(user_id)
        api_request_time = time.time()
        row_data = [single_user_info[key] for key in user_info_keys] + [api_request_time]
        table_rows.append(row_data)
    dataframe = pd.DataFrame(table_rows, columns=column_names_for_table)
    dataframe.set_index('user_id', inplace=True)
    return dataframe

def get_user_feed_table(api, user_id, **api_kwargs):
    """
    Collects media info for each post from user_id through API and formats as pandas dataframe.
    """
    media_info_keys = ['media_id', 'user_id', 'username', 'like_count', 'comment_count', 'time_posted',
                       'num_sliding_content', 'media_type', 'caption_text', 'media_urls', 'tagged_users',]
    column_names_for_table = media_info_keys + ['api_request_time']
    user_feed, next_begin_query_id = api.user_feed(user_id, **api_kwargs)
    api_request_time = time.time()
    table_rows = []
    for single_media_info in user_feed: #loop through different posts (medias)
        row_data = [single_media_info[key] for key in media_info_keys] + [api_request_time]
        table_rows.append(row_data)
    dataframe = pd.DataFrame(table_rows, columns=column_names_for_table)
    dataframe.set_index('media_id', inplace=True)
    return dataframe, next_begin_query_id

def update_csv_file(table, csv_filename):
    if os.path.isfile(csv_filename):
        loaded_table = pd.read_csv(csv_filename, index_col=0, engine='python')
    else:
        loaded_table = None
    new_table = combine_info_tables(table, loaded_table)
    new_table.to_csv(csv_filename)

def combine_info_tables(table1, table2):
    """
    Combines two tables and eliminates duplicates by only keeping most recently collected data
    """
    new_table = pd.concat([table1, table2])
    new_table = new_table.sort_values('api_request_time', ascending=False) #most recent on top
    duplicated_indices = new_table.index.duplicated(keep='first') #all duplicates except the first set to True
    new_table = new_table[~duplicated_indices]
    return new_table

def user_id_in_table(user_id, table):
    """
    Returns true if user_id is in 'user_id' column of table.
    """
    if table is None:
        return False
    else:
        user_ids_present = table.reset_index()['user_id'].values
        user_id_in_table = (user_id in user_ids_present)
        return user_id_in_table