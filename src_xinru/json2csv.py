"""
Chris Bogart
Nov 2018

This program converts collected posts to csv format for discoursedb import
Data location:
    ../data/posts
    ../data/users
    ../data/subreddits

Usage:
    To import posts from a subreddit:
        python json2csv.py --begin <unix_timestamp> -s SUBR_NAME -a AUTHOR_NAME
"""
import json
import os
# prograss bar
from tqdm import tqdm
# command line interface
import click
# import your own config file, see example_config.py
import config
import time
import pytz
import csv
from datetime import datetime

tz = pytz.timezone('UTC')



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

    def retrieve_post(self, post_id):
        assert post_id
        return json.load(open(os.path.join(self.root,'posts', post_id + ".json")))

    def retrieve_posts(self, author=None, subreddit=None):
        assert (author or subreddit) and not (author and subreddit)

        if subreddit is not None:
            foruminfo = self.retrieve_subreddit(subreddit)
            for post_id in foruminfo["posts"]:
                yield self.retrieve_post(post_id)

        if author is not None:
            authorposts = self.retrieve_author(author)
            for post_id in authorposts["posts"]:
                yield self.retrieve_post(post_id)

    def list_authors(self):
        return [fn[:-5] for fn in os.listdir(os.path.join(self.root,'users')) ]

    def list_subreddits(self):
        return [fn[:-5] for fn in os.listdir(os.path.join(self.root,'subreddits')) ]

    def retrieve_author(self, author):
        assert author
        return json.load(open(os.path.join(self.root, 'users', author + ".json")))

    def retrieve_subreddit(self, subreddit):
        assert subreddit
        return json.load(open(os.path.join(self.root, 'subreddits', subreddit + ".json")))

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


def posts2csv(forum_csv, post_csv, begin=None, authors=None, subreddits=None, verbose=True):
    data = Data()

    if subreddits is None:
        subreddits = []
    if subreddits == ["all"]:
        subreddits = data.list_subreddits()
    if authors is None:
        authors = []
    if len(authors) == 1 and authors[0] == "all":
        authors = data.list_authors()
    if begin is None:
        begin = 1100000000.0
    print(authors)


    subredditset = set()

    # subreddit info doesn't seem to have the "subreddit_id".   To do : get that with r/subreddit/<name>/about
    # for now, use subreddit name as forum identifier
    csvf = csv.writer(open(forum_csv,"w"))
    csvf.writerow("forum,forum_name,forum_type,discourse,dataset_file".split(","))
    csvp = csv.writer(open(post_csv,"w"))
    csvp.writerow("id,replyto,username,user_annotation_flairtext,annotation_over18,annotation_score,forum,discourse,title,when,dataset_file,post".split(","))

    for subreddit in subreddits:
        subreddit_info = data.retrieve_subreddit(subreddit)
        csvf.writerow([subreddit,subreddit,"FORUM","Reddit","reddit"])
        subredditset.add(subreddit)
        posts = data.retrieve_posts(subreddit=subreddit)
        for post in posts:
            if post["created"] < begin: continue
            if "selftext" not in post: continue   # Skip URL-only posts
            if "subreddit" not in post:
                print("No subreddit in post " + post["id"])
                continue
            csvp.writerow([post["id"],None,post["author"],post["author_flair_text"],str(post["over_18"]),str(post["score"]),
                           post["subreddit"],"Reddit",post["title"],
                           datetime.fromtimestamp(post["created"], tz).isoformat(),
                           "reddit",post.get("selftext",post["url"])])

    print("NOTE: this retrieves posts after the last retrieval time, but does not capture old posts by new authors")

    for author in authors:
        author_info = data.retrieve_author(author)
        posts = data.retrieve_posts(author=author)
        for post in posts:
            if post["created"] < begin: continue
            if "subreddit" not in post:
                print("No subreddit in post " + post["id"])
                continue
            csvp.writerow([post["id"],None,post["author"],post["author_flair_text"],str(post["over_18"]),str(post["score"]),
                           post["subreddit"],"Reddit",post["title"],
                           datetime.fromtimestamp(post["created"], tz).isoformat(),
                           "reddit",post.get("selftext",post["url"])])
            if post["subreddit"] not in subredditset:
                csvf.writerow([post["subreddit"], post["subreddit"],"FORUM","Reddit","reddit"])
                subredditset.add(post["subreddit"])
        


@click.command()
@click.option( '--commence', type=int, default=1100000000)
@click.option( '-a', '--author', 'authors', type=str, multiple=True, default=[])
@click.option( '-A', '--author-list', 'author_list', type=click.File("r"))
@click.option( '-s', '--subreddit', 'subreddits', type=str, multiple=True, default=[])
@click.option( '-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
def main(commence, authors, author_list, subreddits, subreddit_list):
    if author_list is not None:
        authors = list(authors)
        authors.extend([str(a).strip().split("/")[-1] for a in author_list])
    if subreddit_list is not None:
        subreddits = list(subreddits)
        subreddits.extend([str(s).strip().split("/")[-1] for s in subreddit_list]) 
    posts2csv("forum.csv","posts.csv",commence, authors, subreddits, verbose=True)


if __name__ == '__main__':
    main()

