"""
Xinru Yan
March 2019

This program collects comments for posts given a list of post_ids
Usage:
    python pull_reddit_comment.py -l 1000 -P ../inputs/post_ids.txt > ../log/pull_comments.txt
"""
from psaw import PushshiftAPI
from tqdm import tqdm
from crawl_reddit import Data
import click
import re
from pymongo import MongoClient

api = PushshiftAPI()


class CommentFinder:
    """Given a post_id, retrieve its comments

    """
    def __init__(self, limit, post_id):
        self.post_id = post_id
        self.limit = limit

    def __call__(self):
        args = {'sort': 'asc',
                'sort_type': 'created_utc',
                'limit': self.limit,
                'link_id': self.post_id}

        self.result = api.search_comments(**args)

        return self

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.result)


def grab_more_comments(find_comments):
    comments = []

    for comment in tqdm(find_comments()):
        comments += [comment.d_]

    return comments


def pull_comments(limit, database, post_ids=None):
    if post_ids is None:
        post_ids = []

    data = Data(database)

    for post in tqdm(post_ids):
        comments = grab_more_comments(CommentFinder(limit, post_id=post))
        data.add_comments(comments)
        print(f'pulled {len(comments)} number of comments of post {post}')


def compare(posts, mongodb):
    """Given a list of post_ids, comparing it with a list of post_ids which comments have already been pulled and return
    an updated list of post_ids which comments are needed to be pulled

    :param posts: a list of post_ids
    :return: an updated list of post_ids
    """
    myclient = MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient[mongodb]
    mycol = mydb["comments"]
    pulled_posts = []
    for x in mycol.find({}, {"link_id": 1, "_id": 0}):
        for id in x:
            post_id = re.search(r'(?<=_)\w+', x[id]).group(0)
            pulled_posts.append(post_id)
    updated_posts = list(set(posts) - set(pulled_posts))
    return updated_posts


@click.command()
@click.option('-l', '--limit', 'limit', type=int, default=1000)
@click.option('-p', '--posts', 'posts', type=str, multiple=True)
@click.option('-d', '--database', 'database', type=str)
@click.option('-P', '--posts_list', 'posts_list', type=click.File("r"))
def main(limit, posts, posts_list, database):
    if posts_list is not None:
        posts = list(posts)
        posts.extend([str(post).strip().split("/")[-1] for post in posts_list if post.strip() != ""])
    update_posts = compare(posts, database)
    pull_comments(limit, database, update_posts)


if __name__ == '__main__':
    main()



