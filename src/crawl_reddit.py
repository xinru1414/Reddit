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
# prograss bar
from tqdm import tqdm
# command line interface
import click
# import your own config file, see example_config.py
import config


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
    newest_time = 0

    for post in tqdm(find_posts()):
        posts += [post.d_]
        if post.created_utc > newest_time:
            newest_time = post.created_utc

    return posts, newest_time


def pull_posts(limit, authors=None, subreddits=None):
    if authors is None:
        authors = []
    if subreddits is None:
        subreddits = []

    data = Data()

    for author in authors:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(author=author), author=author))
        data.add_posts(posts, author=author)
        data.set_newest_time(newest_time, author=author)

    for subreddit in subreddits:
        posts, newest_time = grab_more_posts(PostFinder(limit, start=data.get_newest_time(subreddit=subreddit), subreddit=subreddit))
        data.add_posts(posts, subreddit=subreddit)
        data.set_newest_time(newest_time, subreddit=subreddit)


@click.command()
@click.option('-l', '--limit', type=int, default=1000)
@click.option('-a', '--author', 'authors', type=str, multiple=True)
@click.option('-s', '--subreddit', 'subreddits', type=str, multiple=True)

def main(limit, authors, subreddits):
    pull_posts(limit, authors, subreddits)


if __name__ == '__main__':
    main()

