import json
import os

from .post import Post
from .comment import Comment


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

    @property
    def comments(self):
        with open(self.path, 'r') as fp:
            comments = json.load(fp)['comments']
        return (Comment.load_comment(comment_id, self.db_root) for comment_id in comments)
