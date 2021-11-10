from instagram_private_api import Client, ClientCookieExpiredError, ClientLoginRequiredError
import time
import json
import codecs
import os.path
import numpy as np


class SafeClient(Client):
    def __init__(self, username, password, *args, **kwargs):
        if 'max_api_calls_per_hour' in kwargs:
            self.max_api_calls_per_hour = kwargs.pop('max_api_calls_per_hour')
        else:
            official_max = 200
            leeway = 5
            self.max_api_calls_per_hour = official_max - leeway
        if 'api_call_wait_time_generator' in kwargs:
            self.api_call_wait_time_generator = kwargs.pop('api_call_wait_time_generator')
        else:
            #random time for api calls makes bot look more human
            self.api_call_wait_time_generator = lambda : np.random.uniform(low=3.0, high=5.0)

        #Initialize with saved auth cookies if exists or create new login.
        settings_filename = 'saved_info/%s_login_settings.json'%username
        try:
            if not os.path.isfile(settings_filename):
                on_login = lambda x: SafeClient._onlogin_callback(x, settings_filename)
                super().__init__(username, password, *args, on_login=on_login, **kwargs)
            else:
                with open(settings_filename) as file_data:
                    cached_settings = json.load(file_data, object_hook=SafeClient._from_json)
                super().__init__(username, password, *args, settings=cached_settings, **kwargs)
        except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
            print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))
            on_login = lambda x: SafeClient._onlogin_callback(x, settings_filename)
            super().__init__(username, password, *args, on_login=on_login, **kwargs)

        #Create file for keeping api time calls if necessary
        api_call_times_filename = 'saved_info/%s_api_call_times.json'%username
        if not os.path.isfile(api_call_times_filename):
            with open(api_call_times_filename, 'w') as outfile:
                initial_time_list = [0] #give nonempty file for json to read
                json.dump(initial_time_list, outfile)

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
        Safe wrapper for Ping's _call_api method. Program waits, then gives exception if 
        max_api_calls_per_hour have been made in the last hour. Keeps record of most recent 
        api call times in seconds in json file.
        """
        self._api_sleep()
        api_calls_in_seconds = self._load_api_call_times()
        self._check_reached_api_limit(api_calls_in_seconds)
        self._update_api_call_times(api_calls_in_seconds)
        return super()._call_api(*args, **kwargs)

    def _api_sleep(self):
        wait_time = self.api_call_wait_time_generator()
        time.sleep(wait_time)

    def _load_api_call_times(self):
        api_call_times_filename = 'saved_info/%s_api_call_times.json'%self.username
        with open(api_call_times_filename, 'r') as outfile:
            api_calls_in_seconds = json.load(outfile)
        api_calls_in_seconds = api_calls_in_seconds[-self.max_api_calls_per_hour:]
        return api_calls_in_seconds

    def _check_reached_api_limit(self, api_calls_in_seconds):
        oldest_call = api_calls_in_seconds[0]
        seconds_in_hour = 3600
        num_recorded = len(api_calls_in_seconds)
        if time.time()-oldest_call < seconds_in_hour and num_recorded >= self.max_api_calls_per_hour:
            raise Exception('API call limit reached')

    def _update_api_call_times(self, api_calls_in_seconds):
        api_call_times_filename = 'saved_info/%s_api_call_times.json'%self.username
        api_calls_in_seconds.append(time.time())
        with open(api_call_times_filename, 'w') as outfile:
            json.dump(api_calls_in_seconds, outfile)