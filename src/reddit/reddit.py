import os

from .subreddit import Subreddit
from .user import User


class Reddit:
    def __init__(self, db_root):
        self.db_root = db_root

    def get_subreddit(self, name):
        path = os.path.join(self.db_root, 'subreddits', name+'.json')
        if os.path.exists(path):
            return Subreddit(name, self.db_root)
        else:
            return None

    def get_user(self, name):
        path = os.path.join(self.db_root, 'users', name+'.json')
        if os.path.exists(path):
            return User(name, self.db_root)
        else:
            return None

    def get_users(self):
        for user_file in os.listdir(os.path.join(self.db_root, 'users')):
            yield User(os.path.splitext(user_file)[0], self.db_root)
