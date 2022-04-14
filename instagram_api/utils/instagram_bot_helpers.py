import os
import sys
import random
import time
import numpy as np
import pandas as pd
import pyautogui
import cv2
from copy import deepcopy
from pynput.keyboard import (Controller as KeyboardController, Key)
from pyclick import HumanClicker
import pytesseract
from transformers import AutoTokenizer, AutoModelForCausalLM
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, instagram_api_folder)

class AutomatedInstagramSession():
    def __init__(self):
        self.keyboard_controller = KeyboardController()
        self.human_clicker = HumanClicker()
        self.tokenizer = AutoTokenizer.from_pretrained("satvikag/chatbot")
        self.model = AutoModelForCausalLM.from_pretrained("satvikag/chatbot")

    def _get_screenshot_bgr(self):
        screenshot_rgb = pyautogui.screenshot()
        screenshot_rgb = np.array(screenshot_rgb)
        screenshot_bgr = cv2.cvtColor(np.array(screenshot_rgb), cv2.COLOR_RGB2BGR)
        return screenshot_bgr

    def image_to_text(self, image):
        image_resize = cv2.resize(image, (0, 0), fx=2, fy=2)
        image_gray = cv2.cvtColor(image_resize, cv2.COLOR_BGR2GRAY)
        image_threshold = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        text = pytesseract.image_to_string(image_threshold)
        text = text.replace("\x0c", "")
        text = text.replace("\n", "")
        return text

    def type_string_with_delay(self, string):
        """
        Human-like typing on keyboard
        """
        for character in string:
            self.keyboard_controller.type(character)
            delay = random.uniform(0.05, 0.4)
            time.sleep(delay)

    def click_key(self, key_type):
        """
        Presses key on keyboard
        """
        self.keyboard_controller.press(key_type)
        time.sleep(random.uniform(0.1,0.2))
        self.keyboard_controller.release(key_type)

    def get_click_position_from_box(self, top_left_corner_px, bottom_right_corner_px):
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

    def convert_coordinates_to_pixels(self, coordinates):
        """
        Converts between indices on image and pixels on screen
        """
        x_coordinate, y_coordinate = coordinates
        screen_width_px, screen_height_px = pyautogui.size()
        screenshot_height, screenshot_width, _ = np.array(pyautogui.screenshot()).shape
        x_pixels = x_coordinate*screen_width_px/screenshot_width
        y_pixels = y_coordinate*screen_height_px/screenshot_height
        return (x_pixels, y_pixels)

    def convert_pixels_to_coordinates(self, pixels):
        """
        Converts between pixels on screen and indices on image
        """
        x_pixels, y_pixels = pixels
        screen_width_px, screen_height_px = pyautogui.size()
        screenshot_height, screenshot_width, _ = np.array(pyautogui.screenshot()).shape
        x_coordinate = np.array(x_pixels)*screenshot_width/screen_width_px
        y_coordinate = np.array(y_pixels)*screenshot_height/screen_height_px
        return (x_coordinate, y_coordinate)

    def get_box_corners_from_image(self, object_image_filename):
        """
        Gets screenshot, then searches screenshot to find object, returns corners of box containing image.
        """
        #Get screenshot and object to find
        screenshot_bgr = self._get_screenshot_bgr()
        object_image = cv2.imread(object_image_filename)
        #Find object in screenshot
        match_results = cv2.matchTemplate(screenshot_bgr, object_image, cv2.TM_SQDIFF_NORMED)
        #Get coordinates for corners of object
        min_value, _, top_left_corner, _ = cv2.minMaxLoc(match_results)
        object_height, object_width, _ = object_image.shape
        bottom_right_corner = (top_left_corner[0]+object_width, top_left_corner[1]+object_height)
        #Convert coordinates into screen pixels
        top_left_corner = self.convert_coordinates_to_pixels(top_left_corner)
        bottom_right_corner = self.convert_coordinates_to_pixels(bottom_right_corner)
        return (top_left_corner, bottom_right_corner)

    def get_matched_result_image(self, object_filename):
        box_corners = self.get_box_corners_from_image(object_filename)
        box_corners = self.convert_pixels_to_coordinates(box_corners)
        screenshot = np.array(pyautogui.screenshot())
        top_left_corner, bottom_right_corner = box_corners
        min_y, min_x = top_left_corner
        max_y, max_x = bottom_right_corner
        image_in_screenshot = deepcopy(screenshot[int(min_x):int(max_x), int(min_y):int(max_y)])
        return image_in_screenshot

    def _get_black_and_white_screenshot(self):
        screenshot_bgr = self._get_screenshot_bgr()
        #Convert to gray scale
        screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
        #Threshold colors so white stays white, other becomes black
        threshold_value = 245 #just less than white (255)
        white_color_value = 255
        _, screenshot_black_and_white = cv2.threshold(screenshot_gray, threshold_value, white_color_value, cv2.THRESH_BINARY)
        return screenshot_black_and_white

    def _get_contours_on_screenshot(self):
        black_and_white_screenshot = self._get_black_and_white_screenshot()
        contours, _ = cv2.findContours(black_and_white_screenshot, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def get_first_post_corners(self):
        """
        Gets top left and bottom right corner of first post on user's page. Must be on the user's page. Only works if the entire post box 
        is on the screen.
        """
        screenshot_black_and_white = self._get_black_and_white_screenshot()
        #Get contours (lines) in image
        contours, _ = cv2.findContours(screenshot_black_and_white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
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
        top_left_corner = self.convert_coordinates_to_pixels(top_left_corner)
        bottom_right_corner = self.convert_coordinates_to_pixels(bottom_right_corner)
        return (top_left_corner, bottom_right_corner)

    def click_on_box(self, object_image_filename):
        top_left_corner, bottom_right_corner = self.get_box_corners_from_image(object_image_filename)
        click_position = self.get_click_position_from_box(top_left_corner, bottom_right_corner)
        self.human_clicker.move(click_position, random.uniform(0.7, 2))
        time.sleep(random.uniform(0.4, 0.7))
        self.human_clicker.click()

    def move_to_box(self, object_image_filename):
        top_left_corner, bottom_right_corner = self.get_box_corners_from_image(object_image_filename)
        click_position = self.get_click_position_from_box(top_left_corner, bottom_right_corner)
        self.human_clicker.move(click_position, random.uniform(0.7, 2))

    def search_username(self, username):
        self.click_on_box('../instagram_images/search_field.png')
        time.sleep(random.uniform(1.0, 2.0))
        self.type_string_with_delay(username)
        #Select result
        time.sleep(random.uniform(3.0, 4.0))
        self.click_key(Key.enter)
        #Go to results - and check that page changed
        start_page = np.array(pyautogui.screenshot())
        time.sleep(random.uniform(0.4,0.8))
        self.click_key(Key.enter)
        time.sleep(2.0)
        final_page = np.array(pyautogui.screenshot())
        L1_norm_diff = cv2.norm(start_page, final_page, cv2.NORM_L1 ) / (np.prod(start_page.shape))
        if L1_norm_diff < 1:
            print(f'Got L1 diff of {L1_norm_diff} for:')
            return False
        else:
            return True

    def check_if_new_dm(self):
        """
        Checks if there is new DM by searching for blue box, then seeing if in correct location
        """
        #Hand-tuned for my computer
        blue_dot_look_y_min = 500
        blue_dot_look_y_max = 1760
        blue_dot_look_x_min = 1047
        blue_dot_look_x_max = 1205

        top_left_corner_px, bottom_right_corner_px = self.get_box_corners_from_image('../instagram_images/new_message_dot.png')
        top_left_corner_coordinate = self.convert_pixels_to_coordinates(top_left_corner_px)
        bottom_right_corner_coordinate = self.convert_pixels_to_coordinates(bottom_right_corner_px)
        center_x = (bottom_right_corner_coordinate[0]+top_left_corner_coordinate[0])/2
        center_y = (bottom_right_corner_coordinate[1]+top_left_corner_coordinate[1])/2
        if center_x>blue_dot_look_x_min and center_x<blue_dot_look_x_max and center_y>blue_dot_look_y_min and center_y<blue_dot_look_y_max:
            return True
        else:
            return False

    def accept_first_user_request_dm(self):
        top_left_corner, bottom_right_corner = self.get_box_corners_from_image('../instagram_images/requests_arent_marked.png')
        request_arent_marked_position = self.get_click_position_from_box(top_left_corner, bottom_right_corner)
        user_dm_request_location = (request_arent_marked_position[0],request_arent_marked_position[1]+50)
        self.human_clicker.move(user_dm_request_location, random.uniform(0.7, 2))
        time.sleep(random.uniform(0.4, 0.7))
        self.human_clicker.click()
        time.sleep(random.uniform(0.9, 1.4))
        self.click_on_box('../instagram_images/accept_button.png')

    def get_message_to_respond_to(self):
        """
        When on specific user DM page, returns message they sent, or "" if none
        """
        #Hand-picked for my computer
        message_look_x_min = 1462
        message_look_x_max = 1603
        message_look_y_min = 1314
        message_look_y_max = 1787
        screenshot = np.array(pyautogui.screenshot())
        message_crop = screenshot[message_look_x_min:message_look_x_max, message_look_y_min:message_look_y_max]
        message = self.image_to_text(message_crop)
        return message

    def check_for_request_button(self):
        request_button_found = self.get_matched_result_image('../instagram_images/request_dm_button.png')
        request_text = self.image_to_text(request_button_found)
        if request_text == 'Request':
            return True
        else:
            return False

    def are_following_username(self):
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

    def click_on_first_post(self, top_left_corner, bottom_right_corner):
        click_position = self.get_click_position_from_box(top_left_corner, bottom_right_corner)
        self.human_clicker.move(click_position, random.uniform(0.7, 2))
        time.sleep(random.uniform(0.4, 0.7))
        self.human_clicker.click()

    def refresh_page(self):
        self.keyboard_controller.press(Key.cmd)
        time.sleep(random.uniform(0.1,0.2))
        self.keyboard_controller.press(Key.shift)
        time.sleep(random.uniform(0.1,0.2))
        self.keyboard_controller.type('r')
        time.sleep(random.uniform(0.1,0.2))
        self.keyboard_controller.release(Key.shift)
        time.sleep(random.uniform(0.1,0.2))
        self.keyboard_controller.release(Key.cmd)

    def post_typed_comment(self):
        self.click_key(Key.enter)

    def exit_post(self):
        self.click_key(Key.esc)

    def generate_chatbot_response(self, message):
        message_input_ids = self.tokenizer.encode(message + self.tokenizer.eos_token, return_tensors='pt')
        chat_history_ids = self.model.generate(
            message_input_ids, max_length=500,
            pad_token_id=self.tokenizer.eos_token_id,  
            no_repeat_ngram_size=3,       
            do_sample=True, 
            top_k=100, 
            top_p=0.7,
            temperature = 0.8
        )
        response = "{}".format(self.tokenizer.decode(chat_history_ids[:, message_input_ids.shape[-1]:][0], skip_special_tokens=True))
        response = response.replace("Softwaresat", "bot_bot_art")
        return response

    def respond_to_user_dm(self):
        message = self.get_message_to_respond_to()
        if message != '':
            response = self.generate_chatbot_response(message)
            self.click_on_box('../instagram_images/message_button.png')
            time.sleep(random.uniform(1.0, 1.5))
            self.type_string_with_delay(response)
            time.sleep(random.uniform(0.5, 1.0))
            self.post_typed_comment()
            time.sleep(random.uniform(0.5, 1.0))
            self.refresh_page()