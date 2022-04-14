import os
import sys
import time
import random
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)
from utils import instagram_bot_helpers
AutomatedInstagramSession = instagram_bot_helpers.AutomatedInstagramSession

bot = AutomatedInstagramSession()

def respond_to_dm_requests():
    while True:
        if bot.check_for_request_button():
            bot.click_on_box('../instagram_images/request_dm_button.png')
            time.sleep(random.uniform(0.5, 1.0))
            bot.accept_first_user_request_dm()
            time.sleep(random.uniform(0.5, 1.0))
            bot.respond_to_user_dm()
            time.sleep(random.uniform(2.5, 3.5))
        else:
            break

while True:
    time.sleep(random.uniform(9.0, 11.0))
    respond_to_dm_requests()
    if bot.check_if_new_dm():
        bot.click_on_box('../instagram_images/new_message_dot.png')
        time.sleep(random.uniform(0.9, 1.3))
        bot.respond_to_user_dm()
    else:
        bot.refresh_page()

