"""
Wrapper for instagram api Client class to prevent getting banned.
"""
from instagram_private_api import Client, ClientCookieExpiredError, ClientLoginRequiredError
import time
import json
import codecs
import numpy as np
import os
instagram_api_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class SafeClient(Client):
    """
    Safe wrapper for api Client class. Additional features: 
        - Uses cached auth cookies to avoid making API call to relog in
        - Sleeps before making API calls
        - Restricts number of API calls
    """
    def __init__(self, username, password, retry_failed_call = False, *args, **kwargs):
        self.api_call_times_filename = os.path.join(instagram_api_folder, 'saved_info/%s_api_call_times.json'%username)
        self.settings_filename = os.path.join(instagram_api_folder, 'saved_info/%s_login_settings.json'%username)
        self.retry_failed_call = retry_failed_call #If True, when API call limit is reached, program will sleep and then retry.
        if 'max_api_calls_per_hour' in kwargs:
            self.max_api_calls_per_hour = kwargs.pop('max_api_calls_per_hour')
        else:
            official_max = 200
            safety_margin = 120
            self.max_api_calls_per_hour = official_max - safety_margin
        if 'api_call_wait_time_generator' in kwargs:
            self.api_call_wait_time_generator = kwargs.pop('api_call_wait_time_generator')
        else:
            #random time for api calls makes bot look more human
            self.api_call_wait_time_generator = lambda : np.random.uniform(low=3.0, high=4.0) 
        
        #Create file for keeping api call times if doesnt exist
        if not os.path.isfile(self.api_call_times_filename):
            with open(self.api_call_times_filename, 'w') as outfile:
                initial_time_list = [0] #give nonempty file for json to read
                json.dump(initial_time_list, outfile)

        #Initialize with saved auth cookies if exists or create new login.
        try:
            if not os.path.isfile(self.settings_filename):
                on_login = lambda x: SafeClient._onlogin_callback(x, self.settings_filename)
                super().__init__(username, password, *args, on_login=on_login, **kwargs)
            else:
                with open(self.settings_filename) as file_data:
                    cached_settings = json.load(file_data, object_hook=SafeClient._from_json)
                super().__init__(username, password, *args, settings=cached_settings, **kwargs)
        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
            on_login = lambda x: SafeClient._onlogin_callback(x, self.settings_filename)
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


class ApiLimitReachedException(Exception):
    def __init__(self):
        super().__init__('API Limit Reached.')