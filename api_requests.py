from instagram_private_api import Client
from collections import Counter

class BasicUserInfo():
    def __init__(self,api,username):
        self.api = api
        self.username = username
        self.username_info = api.username_info(username)

        self.user_id = self.username_info['user']['pk']
        self.follower_count = self.username_info['user']['follower_count']
        self.following_count = self.username_info['user']['following_count']
        self.media_count = self.username_info['user']['media_count']
        self.private_status = self.username_info['user']['is_private']

class PublicUserInfoRequests(BasicUserInfo):
    def __init__(self,api,username,rank_token):
        super().__init__(api,username)
        self.rank_token = rank_token
        self._error_handling()
    
    def _error_handling(self):
        if self.user_id == int(self.api.authenticated_user_id):
            raise ValueError("Strange behavior when requesting your own info, needs further testing.")
        elif self.private_status:
            raise ValueError("Can't get following info from private account.")

    def _get_user_followers_info(self):
        user_followers_info = []
        begin_query_index = 0
        while True:
            user_followers_query = self.api.user_followers(self.user_id,self.rank_token,max_id=begin_query_index)
            user_followers_info.extend(user_followers_query['users'])
            if 'next_max_id' not in user_followers_query:
                break
            else:
                begin_query_index = user_followers_query['next_max_id']
        return user_followers_info

    def get_followers_usernames(self):
        user_followers_info = self._get_user_followers_info()
        followers_usernames = [follower['username'] for follower in user_followers_info]
        return followers_usernames

    def _get_user_following_info(self):
        user_following_info = []
        begin_query_index = 0
        while True:
            user_following_query = self.api.user_following(self.user_id,self.rank_token,max_id=begin_query_index)
            user_following_info.extend(user_following_query['users'])
            if 'next_max_id' not in user_following_query:
                break
            else:
                begin_query_index = user_following_query['next_max_id']
        return user_following_info

    def get_following_usernames(self):
        user_following_info = self._get_user_following_info()
        following_usernames = [following_user['username'] for following_user in user_following_info]
        return following_usernames

    def get_user_feed_media_ids(self):
        """
        Ordered from most recent to oldest.
        """
        user_feed_media_ids = []
        begin_query_index = 0
        while True:
            user_feed_query = self.api.user_feed(self.user_id,max_id=begin_query_index)        
            media_ids_query = [post['id'] for post in user_feed_query['items']]
            user_feed_media_ids.extend(media_ids_query)
            if 'next_max_id' not in user_feed_query:
                break
            else:
                begin_query_index = user_feed_query['next_max_id']
        return user_feed_media_ids

class MediaInfoRequests():
    def __init__(self,api,media_id,rank_token):
        self.api = api
        self.media_id = media_id
        self.rank_token = rank_token

    def _get_comments_info(self):
        """
        Gets maximum of 150 comments
        """
        return self.api.media_n_comments(self.media_id,n=150,reverse=True)
        
    def get_comment_count(self):
        comments_query = self.api.media_comments(self.media_id)
        comment_count = comments_query['comment_count']
        return comment_count

    def get_n_comments_text(self):
        comments_info = self._get_comments_info()
        comments_text = [comment['text'] for comment in comments_info]
        return comments_text

    def get_n_comment_count_per_username(self):
        comments_info = self._get_comments_info()
        usernames_of_comments = [comment['user']['username'] for comment in comments_info]
        comment_count_per_username = Counter(usernames_of_comments)
        return comment_count_per_username