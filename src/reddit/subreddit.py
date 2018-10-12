import json
import os

from .post import Post


class Subreddit:
    def __init__(self, name, db_root):
        self.name = name
        self.db_root = db_root
        self.path = os.path.join(self.db_root, 'subreddits', name+'.json')

    @property
    def posts(self):
        with open(self.path, 'r') as fp:
            posts = json.load(fp)['posts']
        return (Post.load_post(post_id, self.db_root) for post_id in posts)
