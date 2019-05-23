class Comment:
    @staticmethod
    def load_post(comment_id, db):
        return db.comments.find_one({"id": comment_id})