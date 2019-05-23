class Subreddit:
    def __init__(self, name, db):
        self.name = name
        self.db = db

    @property
    def post_ids(self):
        for rec in self.db.posts.find({"subreddit": self.name}):
            yield rec["id"]

    @property
    def posts(self):
        for rec in self.db.posts.find({"subreddit": self.name}):
            yield rec

    @property
    def comments(self):
        for rec in self.db.comments.find({"subreddit": self.name}):
            yield rec

    def post(self, post_id):
        return self.db.posts.find_one({"id": post_id})

    def comment(self, comment_id):
        return self.db.comments.find_one({"id": comment_id})

    # def top_authors(self, top_n):
    #     users = Counter(post['author'] for post in self.posts)
    #     del users['[deleted]']
    #     return next(zip(*users.most_common(top_n)))
