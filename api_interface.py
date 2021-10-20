from abc import ABC, abstractmethod

class api_session(ABC):

    @property #property means this is an attribute (data) in abstract base class
    @abstractmethod
    def api(self):
        pass

    @property
    @abstractmethod
    def rank_token(self):
        pass

    @abstractmethod
    def get_private_status(self, username: str) -> bool:
        pass

    @abstractmethod
    def get_follower_count(self, username: str) -> int:
        pass

    @abstractmethod
    def get_following_count(self, username: str) -> int:
        pass

    @abstractmethod
    def get_followers_usernames(self, username: str) -> list:
        pass

    @abstractmethod
    def get_following_usernames(self, username: str) -> list:
        pass

    @abstractmethod
    def follow_user(self, username: str) -> None:
        pass

    @abstractmethod
    def unfollow_user(self, username: str) -> None:
        pass

    @abstractmethod
    def like_post(self, media_id: str) -> None:
        pass

    @abstractmethod
    def comment_on_post(self, media_id: str, comment: str) -> None:
        pass