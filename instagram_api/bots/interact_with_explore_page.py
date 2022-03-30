import os
import time
import random
from pynput.keyboard import (Controller as KeyboardController, Key)
from interact_with_users_bot import AutomatedInstagramSession

def get_random_comment():
    random_comment = ''
    comment_building_blocks = [
        ['So adorable! ', 'I love this! ', 'So pretty! ', 'Such a cute post! '],
        ['If you want to look, my account will have lots of cute animal pics ', 'You should check out my account for adorable animal pics ',
        'You should definitely see the amazing pets i posted '],
        ['<3', ':)', '(:', '']
    ]
    for possible_phrase in comment_building_blocks:
        random_comment += random.choice(possible_phrase)
    return random_comment

if __name__ == '__main__':
    bot = AutomatedInstagramSession()
    max_like_count_per_hour = 34
    max_comment_count_per_hour = 15
    like_count = 0
    comment_count = 0
    while(True):
        time.sleep(random.uniform(4.0, 8.0))
        if random.uniform(0.0, 1.0) < 1/2: #1/5: #Like Post
            time.sleep(random.uniform(6.0, 9.0))
            bot.click_on_box('../instagram_images/like_button.png')
            like_count+=1
            time.sleep(random.uniform(3,5))
            if random.uniform(0.0, 1.0) < 1/2: #Comment on Post
                bot.click_on_box('../instagram_images/comment_field.png')
                time.sleep(random.uniform(10.0, 15.0))
                random_comment = get_random_comment()
                bot.type_string_with_delay(random_comment)
                time.sleep(random.uniform(0.5, 2.0))
                bot.post_typed_comment()
                comment_count+=1
                time.sleep(random.uniform(2.0, 4.0))
                print(f'Made {like_count} likes and {comment_count} comments')
        bot.click_key(Key.right) #Move to next post
        if like_count >= max_like_count_per_hour or comment_count >= max_comment_count_per_hour:
            print(f'Made {like_count} likes and {comment_count} comments')
            like_count = 0
            comment_count = 0
            time.sleep(3600)