import json
import os
from collections import Counter

from .post import Post


class Subreddit:
    def __init__(self, name, db_root):
        self.name = name
        self.db_root = db_root
        self.path = os.path.join(self.db_root, 'subreddits', name+'.json')

    @property
    def post_ids(self):
        with open(self.path, 'r') as fp:
            return json.load(fp)['posts']

    @property
    def posts(self):
        for post_id in self.post_ids:
            yield Post.load_post(post_id, self.db_root) 

    def post(self, post_id):
        return Post.load_post(post_id, self.db_root) 

    def top_authors(self, top_n):
        users = Counter(post['author'] for post in self.posts)
        del users['[deleted]']
        return next(zip(*users.most_common(top_n)))

