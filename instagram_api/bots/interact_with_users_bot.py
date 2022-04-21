import os
import sys
import random
import time
import numpy as np
import pandas as pd
from pynput.keyboard import Key
from copy import deepcopy
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils import instagram_bot_helpers
AutomatedInstagramSession = instagram_bot_helpers.AutomatedInstagramSession

if __name__ == '__main__':
    bot = AutomatedInstagramSession()

    #Load media table
    api_username = 'cuteanimalzzzz123'
    media_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_media_info_table.csv'%api_username)
    if os.path.isfile(media_table_filename):
        loaded_media_table = pd.read_csv(media_table_filename, index_col=0)
    else:
        loaded_media_table = None
    usernames_to_interact_with = loaded_media_table['username'].unique()
    for username in usernames_to_interact_with[200:300]:
        time.sleep(3)
        search_succesful = bot.search_username(username)
        if search_succesful == False:
            print(f'Failed searching username {username}')
            continue
        time.sleep(random.uniform(0.5, 1.0))
        if not bot.are_following_username():
            bot.click_on_box('../instagram_images/follow_button.png')
            time.sleep(random.uniform(1.0, 2.0))
        for _ in range(4):
            first_post_corners = bot.get_first_post_corners()
            if first_post_corners != None:
                bot.click_on_first_post(*first_post_corners)
                time.sleep(random.uniform(1.5, 2.0))
                bot.click_on_box('../instagram_images/like_button.png')
                time.sleep(random.uniform(0.5, 1.0))
                bot.click_on_box('../instagram_images/comment_field.png')
                time.sleep(random.uniform(0.5, 1.0))
                comment = 'Hey, Id love to connect!'
                bot.type_string_with_delay(comment)
                time.sleep(random.uniform(0.5, 1.0))
                bot.post_typed_comment()
                time.sleep(random.uniform(1.0, 2.0))
                bot.exit_post()
                break
            else:
                [bot.click_key(Key.down) for _ in range(5)]
                time.sleep(0.5)
        if not bot.are_following_username(): #This function is buggy
            print('Didnt follow user')