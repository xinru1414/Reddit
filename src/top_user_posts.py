"""
Xinru Yan
Sept 2018

Pull the top-n users's posts from a given subreddit
Data location:
    ../data/users/
    

Usage:
    To pull all posts of top-20 users from a given subreddit:
        python top_user_posts.py -s SUBR_NAME -n 20
"""
from reddit import Reddit
import config
import click
from crawl_reddit import pull_posts
from collections import Counter


@click.command()
@click.option('-s', '--subreddit', type=str)
@click.option('-n', '--top-n', type=int, default=10)
def main(subreddit, top_n):
    reddit = Reddit(config.data_location)

    subr = reddit.get_subreddit(subreddit)
    users = Counter(post['author'] for post in subr.posts)
    # remove deleted account
    del users['[deleted]']
    top_authors = next(zip(*users.most_common(top_n)))

    print('Pulling the following authors...')
    print('\n'.join(top_authors))
    print(top_authors)

    # pull 1000 posts for each user each time
    pull_posts(1000, authors=top_authors)


if __name__ == '__main__':
    main()
