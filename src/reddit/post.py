import json
import os


class Post:
    @staticmethod
    def load_post(post_id, db_root):
        with open(os.path.join(db_root, 'posts', post_id+".json"), 'r') as fp:
            return json.load(fp)
