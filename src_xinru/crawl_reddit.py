"""
Xinru Yan
Sep 2018

This program collects reddit posts per user(author) or per subreddit
Data location:
    ../data/posts
    ../data/users
    ../data/subreddits

Usage:
    To collect posts by one user:
        python crawl_reddit.py -l 1000 -a USER_NAME
    To collect posts by multiple users:
        python crawl_reddit.py -l 1000 -a USER_NAME -a USERNAME
    To collect posts by subreddit:
        python crawl_reddit.py -l 1000 -s SUBR_NAME
    TO collect posts by multiple subreddits:
        python craw_reddit.py -l 1000 -s SUBR_NAME -s SUBR_NAME
"""
from psaw import PushshiftAPI
import json
import os
from tqdm import tqdm
import click
import config
import time


api = PushshiftAPI()


class Data:
    def __init__(self, root=config.data_location):
        self.root = root

        if not os.path.exists(self.root):
            os.mkdir(self.root)

        for i in ['users', 'posts', 'subreddits']:
            if not os.path.exists(os.path.join(self.root, i)):
                os.mkdir(os.path.join(self.root, i))

    def get_newest_time(self, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        path = ''
        if author:
            path = os.path.join(self.root, 'users', author + '.json')
        if subreddit:
            path = os.path.join(self.root, 'subreddits', subreddit + '.json')

        if os.path.exists(path):
            with open(path, 'r') as fp:
                return json.load(fp)['newest_time']
        return 0

    def set_newest_time(self, newest_time, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        path = ''
        if author:
            path = os.path.join(self.root, 'users', author + '.json')
        if subreddit:
            path = os.path.join(self.root, 'subreddits', subreddit + '.json')

        if os.path.exists(path):
            with open(path, 'r') as fp:
                obj = json.load(fp)
        else:
            obj = {}

        obj['newest_time'] = newest_time
        with open(path, 'w') as fp:
            json.dump(obj, fp)

    def add_posts(self, posts, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        # Save posts
        for post in posts:
            path = os.path.join(self.root, 'posts', post['id'] + '.json')
            with open(path, 'w') as fp:
                json.dump(post, fp)

        # Update post lists
        path = ''
        if author:
            path = os.path.join(self.root, 'users', author + '.json')
        if subreddit:
            path = os.path.join(self.root, 'subreddits', subreddit + '.json')

        if os.path.exists(path):
            with open(path, 'r') as fp:
                obj = json.load(fp)
        else:
            obj = {'posts': []}

        obj['posts'] += [post['id'] for post in posts]
        with open(path, 'w') as fp:
            json.dump(obj, fp)

    def add_comments(self, post_id, comments):
        # Save comments
        for comment in comments:
            path = os.path.join(self.root, 'comments', comment['id'] + '.json')
            with open(path, 'w') as fp:
                json.dump(comment, fp)

        # update comments for posts dir
        post_dir = os.path.join(self.root, 'comments_for_posts', post_id)
        if not os.path.exists(post_dir):
            os.mkdir(post_dir)

        for comment in comments:
            comment_path = os.path.join(post_dir, comment['id'])
            if not os.path.exists(comment_path):
                os.mkdir(comment_path)


class PostFinder:
    def __init__(self, limit, start, author=None, subreddit=None):
        self.limit = limit
        self.start = start
        self.author = author
        self.subreddit = subreddit
        self.result = iter([])

    def __call__(self):
        args = {'sort': 'asc',
                'sort_type': 'created_utc',
                'after': self.start,
                'limit': self.limit}
        if self.author:
            args['author'] = self.author
        if self.subreddit:
            args['subreddit'] = self.subreddit

        self.result = api.search_submissions(**args)

        return self

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.result)

    def __len__(self):
        return self.limit


def grab_more_posts(find_posts):
    posts = []
    newest_time = find_posts.start

    for post in tqdm(find_posts()):
        posts += [post.d_]
        if post.created_utc > newest_time:
            newest_time = post.created_utc

    return posts, newest_time


def pull_posts(limit, authors=None, subreddits=None, verbose=True):
    if authors is None:
        authors = []
    if subreddits is None:
        subreddits = []

    data = Data()

    for author in authors:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(author=author), author=author))
        data.add_posts(posts, author=author)
        data.set_newest_time(newest_time, author=author)
        print(f'Last post pulled for author "{author}" was posted on {time.ctime(newest_time)}')

    for subreddit in subreddits:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(subreddit=subreddit), subreddit=subreddit))
        data.add_posts(posts, subreddit=subreddit)
        data.set_newest_time(newest_time, subreddit=subreddit)
        print(f'Last post pulled for subreddit "{subreddit}" was posted on {time.ctime(newest_time)}')


@click.command()
@click.option('-l', '--limit', type=int, default=1000)
@click.option('-a', '--author', 'authors', type=str, multiple=True)
@click.option('-s', '--subreddit', 'subreddits', type=str, multiple=True)
def main(limit, authors, subreddits):
    pull_posts(limit, authors, subreddits, verbose=True)


if __name__ == '__main__':
    main()

