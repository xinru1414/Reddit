import json
from pathlib import Path


class Comment:
    @staticmethod
    def load_comment(comment_id, db_root):
        with open(Path(db_root, 'comments', comment_id, '.json'), 'r') as fp:
            return json.load(fp)
