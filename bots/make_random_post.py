"""
Makes instagram post with random image and quote for caption.
"""
import requests
import random
import datetime
from instauto.api.client import ApiClient
from instauto.helpers.post import upload_image_to_feed
import os
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Log in with instauto package
username = 'ds_club_2021'
password = 'instabotOP'
client = ApiClient(username=username, password=password)
client.log_in()

#Get random photo
photo_request = requests.get('https://picsum.photos/800/800') #request random 800x800 photo
photo_bytes = photo_request.content

#Save random photo
saved_images_folder = os.path.join(instagram_api_folder, 'saved_info/images_for_posting')
image_filename = datetime.datetime.now().strftime("%m_%d_%Y__%H_%M_%S")+'.jpg' #Example: '12_22_2021__16_48_19.jpg'
image_full_filename = os.path.join(saved_images_folder, image_filename)
with open(image_full_filename, mode='wb') as image_file:
    image_file.write(photo_bytes) #save photo

#Get random caption
quote_request = requests.get('https://type.fit/api/quotes') #request list of random quotes
quote_list = quote_request.json()
random_quote = random.choice(quote_list)
caption = random_quote['text']
if random_quote['author'] is not None:
    caption += '- %s'%random_quote['author']

#Post photo to instagram
upload_image_to_feed(client, image_full_filename, caption)
