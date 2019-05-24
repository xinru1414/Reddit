class Post:
    @staticmethod
    def load_post(post_id, db):
        return db.posts.find_one({"id": post_id})
