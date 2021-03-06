"""
Wrapper for Ping's instagram api Client class which adds additional features. Should use SafeClientExtended() class for data collection.
"""
from instagram_private_api import Client, ClientCookieExpiredError, ClientLoginRequiredError
import time
import json
import codecs
import numpy as np
import functools
import os
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SafeClient(Client):
    """
    Safe wrapper for api Client class. Additional features: 
        - Uses cached auth cookies to avoid making API call to relog in
        - Sleeps before making API calls
        - Restricts number of API calls per hour
    """
    def __init__(self, username, *args, retry_failed_call = False, **kwargs):
        self.retry_failed_call = retry_failed_call #If True, when API call limit is reached, program will sleep and then retry.
        
        #Check for keyword arguments
        if 'max_api_calls_per_hour' in kwargs:
            self.max_api_calls_per_hour = kwargs.pop('max_api_calls_per_hour')
        else:
            official_max = 200
            safety_margin = 40
            self.max_api_calls_per_hour = official_max - safety_margin
        if 'api_call_wait_time_generator' in kwargs:
            self.api_call_wait_time_generator = kwargs.pop('api_call_wait_time_generator')
        else:
            #random time for api calls makes bot look more human
            self.api_call_wait_time_generator = lambda : np.random.uniform(low=3.0, high=4.0) 

        self.api_call_times_filename = os.path.join(instagram_api_folder, 'saved_info/%s_api_call_times.json'%username)
        if not os.path.isfile(self.api_call_times_filename):
            self._create_api_call_times_file()
        password = self._get_password(username)
        self._login_with_cached_data(username, password, *args, **kwargs)

    def _create_api_call_times_file(self):
        with open(self.api_call_times_filename, 'w') as outfile:
                initial_time_list = [0] #give nonempty file for json to read
                json.dump(initial_time_list, outfile)
    
    def _get_password(self, username):
        usernames_passwords_filename = os.path.join(instagram_api_folder, 'saved_info', 'usernames_passwords.txt')
        with open(usernames_passwords_filename, 'r') as usernames_passwords_file:
            usernames_passwords = json.load(usernames_passwords_file)
        password = usernames_passwords.get(username)
        if password == None:
            raise PasswordNotDefinedException()
        return password

    def _login_with_cached_data(self, username, password, *args, **kwargs):
        settings_filename = os.path.join(instagram_api_folder, 'saved_info/%s_login_settings.json'%username)
        try:
            if not os.path.isfile(settings_filename): #create new login
                on_login = lambda x: SafeClient._onlogin_callback(x, settings_filename)
                super().__init__(username, password, *args, on_login=on_login, **kwargs)
            else: #load login data
                with open(settings_filename) as file_data:
                    cached_settings = json.load(file_data, object_hook=SafeClient._from_json)
                super().__init__(username, password, *args, settings=cached_settings, **kwargs)
        except (ClientCookieExpiredError, ClientLoginRequiredError) as e: #error logging in
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
            on_login = lambda x: SafeClient._onlogin_callback(x, settings_filename)
            super().__init__(username, password, *args, on_login=on_login, **kwargs)

    @staticmethod
    def _to_json(python_object):
        if isinstance(python_object, bytes):
            return {'__class__': 'bytes',
                    '__value__': codecs.encode(python_object, 'base64').decode()}
        raise TypeError(repr(python_object) + ' is not JSON serializable')

    @staticmethod
    def _from_json(json_object):
        if '__class__' in json_object and json_object['__class__'] == 'bytes':
            return codecs.decode(json_object['__value__'].encode(), 'base64')
        return json_object

    @staticmethod
    def _onlogin_callback(api, new_settings_file):
        cache_settings = api.settings
        with open(new_settings_file, 'w') as outfile:
            json.dump(cache_settings, outfile, default=SafeClient._to_json)

    def _call_api(self, *args, **kwargs):
        """
        Safe wrapper for Ping's _call_api method. Program waits, then either gives exception or waits and retries
        if max_api_calls_per_hour have been made in the last hour. Keeps record of most recent api call times 
        in seconds in json file.
        """
        self._api_sleep()
        api_calls_in_seconds = self._load_api_call_times()
        while True: #only loops if reached api limit and retry_failed_call is True
            if not self._reached_api_limit(api_calls_in_seconds):
                break
            elif self.retry_failed_call:
                time.sleep(60)
            else:
                raise ApiLimitReachedException()
        self._update_api_call_times(api_calls_in_seconds)
        return super()._call_api(*args, **kwargs)

    def _api_sleep(self):
        wait_time = self.api_call_wait_time_generator()
        time.sleep(wait_time)

    def _load_api_call_times(self):
        with open(self.api_call_times_filename, 'r') as outfile:
            api_calls_in_seconds = json.load(outfile)
        api_calls_in_seconds = api_calls_in_seconds[-int(1e4):] #limit to number of clock times saved
        return api_calls_in_seconds

    def _reached_api_limit(self, api_calls_in_seconds):
        """
        Returns True if max_api_calls_per_hour is reached in an hour, otherwise False
        """
        num_recorded = len(api_calls_in_seconds)
        if num_recorded < self.max_api_calls_per_hour:
            return False
        oldest_relevant_call = api_calls_in_seconds[-self.max_api_calls_per_hour]
        time_since_oldest_relevant_call = time.time()-oldest_relevant_call
        seconds_in_hour = 3600
        return (time_since_oldest_relevant_call < seconds_in_hour)

    def _update_api_call_times(self, api_calls_in_seconds):
        api_calls_in_seconds.append(time.time())
        with open(self.api_call_times_filename, 'w') as outfile:
            json.dump(api_calls_in_seconds, outfile)


class SafeClientExtended(SafeClient):
    """
    Extension to the SafeClient API class. Additional features:
        - Formats output of API calls for easier data collection.
        - Added keyword arguments to API calls to help page through long list of results.
        - Safety check that API call doesn't request inaccessible info from private user.
    """
    def __init__(self, *args, allow_checking_friends = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_checking_user_ids = [] #additional user ids which are safe to get info from
        if allow_checking_friends:
            self.allow_checking_user_ids = [int(self.authenticated_user_id)]
            api_user_following, _ = self.user_following(self.authenticated_user_id)
            self.allow_checking_user_ids.extend(api_user_following)

    def _pagination(api_function):
        """
        Some functions require loading more page results. This python decorator does this automatically with multiple API calls.
        """
        @functools.wraps(api_function)
        def api_function_wrapper(*args, begin_query_id = None, num_results_stop_api_at = 1e5, **kwargs):
            output = []
            while True:
                single_query_output, begin_query_id = api_function(*args, begin_query_id = begin_query_id, **kwargs)
                [output.append(x) for x in single_query_output if x not in output] #don't add duplicate results to output
                if len(output) >= num_results_stop_api_at or begin_query_id == None:
                    break
            return output, begin_query_id
        return api_function_wrapper

    def user_info(self, user_id):
        """
        Returns dictionary of useful user info from user id.
        """
        output = super().user_info(user_id)
        output_formatted = self._format_user_info_output(output)
        return output_formatted

    def username_info(self, username):
        """
        Returns dictionary of useful user info from username.
        """
        output = super().username_info(username)
        output_formatted = self._format_user_info_output(output)
        return output_formatted

    def _format_user_info_output(self, output):
        output_formatted = {
                'username' : output['user']['username'],
                'user_id' : output['user']['pk'],
                'full_name' : output['user']['full_name'],
                'private_status' : output['user']['is_private'],
                'profile_pic_url' : output['user']['profile_pic_url'],
                'media_count' : output['user']['media_count'],
                'follower_count' : output['user']['follower_count'],
                'following_count' : output['user']['following_count'],
                'bio_text' : output['user']['biography'],
                'url_in_bio' : output['user']['external_url'],
                'hashtag_following_count' : output['user']['following_tag_count'],
                'usertags_count' : output['user']['usertags_count']
            }
        return output_formatted

    def user_followers(self, user_id, begin_query_id = None, return_username = False, **kwargs):
        """
        Returns list of user ids of followers and the next begin query id (for pagination).
        """
        self._user_id_error_handling(user_id)
        rank_token = super().generate_uuid()
        output_formatted, next_begin_query_id = self._user_followers(user_id, rank_token, begin_query_id = begin_query_id, 
                                                                    return_username = return_username, **kwargs)
        return output_formatted, next_begin_query_id

    @_pagination
    def _user_followers(self, user_id, rank_token, begin_query_id = None, return_username = False, **kwargs):
        output = super().user_followers(user_id, rank_token, max_id = begin_query_id, return_username = return_username, **kwargs)
        next_begin_query_id = output.get('next_max_id')
        output_formatted = self._format_follow_info_output(output, return_username)
        return output_formatted, next_begin_query_id

    def user_following(self, user_id, begin_query_id = None, return_username = False, **kwargs):
        """
        Returns list of user ids of following and the next begin query id (for pagination).
        """
        self._user_id_error_handling(user_id)
        rank_token = super().generate_uuid()
        output_formatted, next_begin_query_id = self._user_following(user_id, rank_token, begin_query_id = begin_query_id, 
                                                                    return_username = return_username, **kwargs)
        return output_formatted, next_begin_query_id

    @_pagination
    def _user_following(self, user_id, rank_token, begin_query_id = None, return_username = False, **kwargs):
        output = super().user_following(user_id, rank_token, max_id = begin_query_id, **kwargs)
        next_begin_query_id = output.get('next_max_id')
        output_formatted = self._format_follow_info_output(output, return_username)
        return output_formatted, next_begin_query_id

    def _format_follow_info_output(self, output, return_username):
        if not return_username: #returns user_id
            output_formatted = [follow['pk'] for follow in output['users']]
        else: #return user_id and username
            output_formatted = [[follow['pk'], follow['username']] for follow in output['users']]
        return output_formatted

    def user_feed(self, user_id, begin_query_id = None, **kwargs):
        """
        Returns list (where each element is a different post) of dictionaries (each contains post info),
        and next begin query id (for pagination).
        """
        self._user_id_error_handling(user_id)
        output_formatted, next_begin_query_index = self._user_feed(user_id, begin_query_id = begin_query_id, **kwargs)
        return output_formatted, next_begin_query_index

    @_pagination
    def _user_feed(self, user_id, begin_query_id = None, **kwargs):
        output = super().user_feed(user_id, max_id = begin_query_id, **kwargs)
        next_begin_query_id = output.get('next_max_id')
        output_formatted = self._format_user_feed_output(output)
        return output_formatted, next_begin_query_id

    def _format_user_feed_output(self, output):
        output_formatted = []
        for media in output['items']:
            media_output = {
                'media_id' : media.get('id'),
                'username' : media.get('user').get('username'),
                'user_id' : media.get('user').get('pk'),
                'like_count' : media.get('like_count'),
                'comment_count' : media.get('comment_count'),
                'time_posted' : media.get('taken_at'),
                'num_sliding_content' : media.get('carousel_media_count', 1),
                'media_type' : media.get('media_type')
            }
            #Check for caption
            if media.get('caption') != None:
                media_output['caption_text'] = media['caption'].get('text')
            else:
                media_output['caption_text'] = None
            #Get URL for medias
            if media_output['num_sliding_content'] == 1:
                media_output['media_urls'] = [media['image_versions2']['candidates'][0]['url']]
            else:
                media_output['media_urls'] = [single_image['image_versions2']['candidates'][0]['url'] for single_image in media['carousel_media']]
            #Get tagged users in each post
            if media_output['num_sliding_content'] == 1:
                if media.get('usertags') == None:
                    media_output['tagged_users'] = None
                else:
                    media_output['tagged_users'] = [user['user']['pk'] for user in media['usertags']['in']]
            else:
                tagged_users = []
                for single_image in media['carousel_media']:
                    if single_image.get('usertags') != None:
                        tagged_users.extend([user['user']['pk'] for user in single_image['usertags']['in']])
                tagged_users_no_duplicates = []
                [tagged_users_no_duplicates.append(user) for user in tagged_users if user not in tagged_users_no_duplicates]
                if len(tagged_users_no_duplicates) == 0:
                    media_output['tagged_users'] = None
                else:
                    media_output['tagged_users'] = tagged_users_no_duplicates
            output_formatted.append(media_output)
        return output_formatted

    def _user_id_error_handling(self, user_id):
        if user_id in self.allow_checking_user_ids:
            return
        if user_id == int(self.authenticated_user_id):
            raise RequestingBadInfoException("Strange behavior when requesting your own info, needs further testing.")
        private_status = self.user_info(user_id)['private_status']
        if private_status:
            raise RequestingBadInfoException("Can't get this info from private account.")

    def media_likers(self, media_id):
        """
        Returns partial list of user ids who liked a media post. Same amount as publicly visible on Instagram App.
        """
        output = super().media_likers(media_id)
        formatted_output = self._format_media_likers_output(output)
        return formatted_output

    def _format_media_likers_output(self, output):
        output_formatted = [user['pk'] for user in output['users']]
        return output_formatted

    def media_comments(self, media_id, num_results_stop_api_at=100):
        output = super().media_n_comments(media_id, n=num_results_stop_api_at)
        output_formatted = self._format_media_comments(output)
        return output_formatted

    def _format_media_comments(self, output):
        formatted_output = [
            {
                'user_id': comment['user_id'], 
                'time_posted': comment['created_at_utc'], 
                'text': comment['text']
                }
            for comment in output
        ]
        return formatted_output


class PasswordNotDefinedException(Exception):
    def __init__(self):
        super().__init__('Password not defined in usernames_passwords file')


class ApiLimitReachedException(Exception):
    def __init__(self):
        super().__init__('API Limit Reached.')


class RequestingBadInfoException(Exception):
    def __init__(self, msg):
        super().__init__(msg)