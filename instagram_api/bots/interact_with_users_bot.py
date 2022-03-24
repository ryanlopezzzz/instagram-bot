import os
import sys
import random
import time
import numpy as np
import pandas as pd
import pyautogui
import cv2
from pynput.keyboard import (Controller as KeyboardController, Key)
from pyclick import HumanClicker
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)

def type_string_with_delay(string, keyboard_controller):
    """
    Human-like typing on keyboard
    """
    for character in string:
        keyboard_controller.type(character)
        delay = random.uniform(0.05, 0.4)
        time.sleep(delay)

def click_key(key_type, keyboard_controller):
    """
    Presses key on keyboard
    """
    keyboard_controller.press(key_type)
    time.sleep(random.uniform(0.1,0.2))
    keyboard_controller.release(key_type)

def get_click_position_from_box(top_left_corner_px, bottom_right_corner_px):
    """
    Generate random position (normally distributed) on box to click
    """
    box_center_x = (top_left_corner_px[0]+bottom_right_corner_px[0])/2
    box_center_y = (top_left_corner_px[1]+bottom_right_corner_px[1])/2
    box_length_x = bottom_right_corner_px[0]-top_left_corner_px[0]
    box_length_y = bottom_right_corner_px[1]-top_left_corner_px[0]
    click_position_x = random.normalvariate(box_center_x, box_length_x/12)
    click_position_y = random.normalvariate(box_center_y, box_length_y/12)
    #Make sure still inside box
    click_position_x = min(click_position_x, bottom_right_corner_px[0])
    click_position_x = max(click_position_x, top_left_corner_px[0])
    click_position_y = min(click_position_y, bottom_right_corner_px[1])
    click_position_y = max(click_position_y, top_left_corner_px[1])
    return (int(click_position_x), int(click_position_y))

def get_box_corners_from_image(object_image_filename):
    """
    Gets screenshot, then searches screenshot to find object, returns corners of box containing image.
    """
    #Get screenshot and object to find
    screenshot_rgb = pyautogui.screenshot()
    screenshot_bgr = cv2.cvtColor(np.array(screenshot_rgb), cv2.COLOR_RGB2BGR)
    object_image = cv2.imread(object_image_filename)
    #Find object in screenshot
    match_results = cv2.matchTemplate(screenshot_bgr, object_image, cv2.TM_SQDIFF_NORMED)
    #Get coordinates for corners of object
    min_value, _, top_left_corner, _ = cv2.minMaxLoc(match_results)
    object_height, object_width, _ = object_image.shape
    bottom_right_corner = top_left_corner[0]+object_width, top_left_corner[1]+object_height
    #Convert coordinates into screen pixels
    screen_width_px, screen_height_px = pyautogui.size()
    screenshot_height, screenshot_width, _ = screenshot_bgr.shape
    top_left_corner = (
        top_left_corner[0]*screen_width_px/screenshot_width, 
        top_left_corner[1]*screen_height_px/screenshot_height
    )
    bottom_right_corner = (
        bottom_right_corner[0]*screen_width_px/screenshot_width,
        bottom_right_corner[1]*screen_height_px/screenshot_height
    )
    return (top_left_corner, bottom_right_corner)

def get_first_post_corners():
    """
    Gets top left and bottom right corner of first post on user's page. Must be on the user's page. Only works if the entire post box 
    is on the screen.
    """
    #Take screenshot
    screenshot = np.array(pyautogui.screenshot())
    #Convert to gray scale
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)
    #Threshold colors so white stays white, other becomes black
    threshold_value = 245 #just less than white (255)
    white_color_value = 255
    _, screenshot_binary = cv2.threshold(screenshot_gray, threshold_value, white_color_value, cv2.THRESH_BINARY)
    #Get contours (lines) in image
    contours, _ = cv2.findContours(screenshot_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #get boxes around each contour. Indices: post num, (top_left_x, top_left_y, width, height)
    bounding_rectangles = np.array([cv2.boundingRect(contour) for contour in contours])
    #identify which boxes have size of post
    post_height = 588
    post_width = 588
    margin_for_error = 10
    bounding_rectangles_widths = bounding_rectangles[:,2]
    bounding_rectangles_heights = bounding_rectangles[:,3]
    has_post_width = (abs(bounding_rectangles_widths-post_width) <= margin_for_error)
    has_post_height = (abs(bounding_rectangles_heights-post_height) <= margin_for_error)
    post_rectangles = bounding_rectangles[has_post_width & has_post_height]
    #Stop if no posts found
    if len(post_rectangles) == 0:
        return None
    #Get first post (further left)
    top_left_x_position = post_rectangles[:,0]
    first_post_rectangle = post_rectangles[np.argmin(top_left_x_position)]
    #Get corners of first post
    top_left_corner = first_post_rectangle[:2]
    bottom_right_corner = top_left_corner+first_post_rectangle[2:]
    #Convert coordinates into screen pixels
    screen_width_px, screen_height_px = pyautogui.size()
    screenshot_height, screenshot_width, _ = screenshot.shape
    top_left_corner = (
        top_left_corner[0]*screen_width_px/screenshot_width, 
        top_left_corner[1]*screen_height_px/screenshot_height
    )
    bottom_right_corner = (
        bottom_right_corner[0]*screen_width_px/screenshot_width,
        bottom_right_corner[1]*screen_height_px/screenshot_height
    )
    return (top_left_corner, bottom_right_corner)

def click_on_box(object_image_filename, human_clicker):
    top_left_corner, bottom_right_corner = get_box_corners_from_image(object_image_filename)
    click_position = get_click_position_from_box(top_left_corner, bottom_right_corner)
    human_clicker.move(click_position, random.uniform(0.7, 2))
    time.sleep(random.uniform(0.4, 0.7))
    human_clicker.click()

def move_to_box(object_image_filename, human_clicker):
    top_left_corner, bottom_right_corner = get_box_corners_from_image(object_image_filename)
    click_position = get_click_position_from_box(top_left_corner, bottom_right_corner)
    human_clicker.move(click_position, random.uniform(0.7, 2))

def search_username(username, human_clicker, keyboard_controller):
    click_on_box('../instagram_images/search_field.png', human_clicker)
    time.sleep(random.uniform(1.0, 2.0))
    type_string_with_delay(username, keyboard_controller)
    #Press enter key twice to click on first result of search
    time.sleep(random.uniform(3.0, 4.0))
    click_key(Key.enter, keyboard_controller)
    time.sleep(random.uniform(0.4,0.8))
    click_key(Key.enter, keyboard_controller)

def are_following_username():
    """
    Before calling this function, must be on that user's page
    """
    #Get screenshot and object to find
    screenshot_rgb = pyautogui.screenshot()
    screenshot_bgr = cv2.cvtColor(np.array(screenshot_rgb), cv2.COLOR_RGB2BGR)
    follow_button_image = cv2.imread('../instagram_images/follow_button.png')
    have_followed_button_image = cv2.imread('../instagram_images/have_followed_button.png')
    follow_match_results = cv2.matchTemplate(screenshot_bgr, follow_button_image, cv2.TM_SQDIFF_NORMED)
    follow_min_value, _, _, _ = cv2.minMaxLoc(follow_match_results)
    have_followed_match_results = cv2.matchTemplate(screenshot_bgr, have_followed_button_image, cv2.TM_SQDIFF_NORMED)
    have_followed_min_value, _, _, _ = cv2.minMaxLoc(have_followed_match_results)
    if have_followed_min_value < follow_min_value:
        return True
    else:
        return False

def click_on_first_post(top_left_corner, bottom_right_corner, human_clicker):
    click_position = get_click_position_from_box(top_left_corner, bottom_right_corner)
    human_clicker.move(click_position, random.uniform(0.7, 2))
    time.sleep(random.uniform(0.4, 0.7))
    human_clicker.click()

def post_typed_comment(keyboard_controller):
    click_key(Key.enter, keyboard_controller)

def exit_post(keyboard_controller):
    click_key(Key.esc, keyboard_controller)

if __name__ == '__main__':
    human_clicker = HumanClicker()
    keyboard_controller = KeyboardController()

    #Load media table
    api_username = 'cuteanimalzzzz123'
    media_table_filename = os.path.join(instagram_api_folder, 'saved_info/%s_collected_media_info_table.csv'%api_username)
    if os.path.isfile(media_table_filename):
        loaded_media_table = pd.read_csv(media_table_filename, index_col=0)
    else:
        loaded_media_table = None
    usernames_to_interact_with = loaded_media_table['username'].unique()
    for username in usernames_to_interact_with[14:30]:
        time.sleep(3)
        search_username(username, human_clicker, keyboard_controller)
        time.sleep(random.uniform(1.0, 2.0))
        first_post_corners = get_first_post_corners()
        if first_post_corners != None:
            click_on_first_post(*first_post_corners, human_clicker)
            time.sleep(random.uniform(1.0, 2.0))
            click_on_box('../instagram_images/like_button.png', human_clicker)
            time.sleep(random.uniform(1.0, 2.0))
            click_on_box('../instagram_images/comment_field.png', human_clicker)
            time.sleep(random.uniform(1.0, 2.0))
            comment = 'Hey! Im new to instagram and would love to make some friends.'
            type_string_with_delay(comment, keyboard_controller)
            time.sleep(random.uniform(1.0, 2.0))
            post_typed_comment(keyboard_controller)
            time.sleep(random.uniform(2.0, 3.0))
            exit_post(keyboard_controller)
        if not are_following_username():
            click_on_box('../instagram_images/follow_button.png', human_clicker)
            time.sleep(random.uniform(3.0, 4.0))
        if not are_following_username():
            print('Didnt follow user')