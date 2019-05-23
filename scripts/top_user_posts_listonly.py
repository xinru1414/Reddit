"""
Xinru Yan
Sept 2018

List the top-n userss from a given subreddit
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
@click.option('-s', '--subreddits', type=str, multiple=True, default=[])
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
@click.option('-n', '--top-n', type=int, default=10)
def main(subreddits, subreddit_list, top_n):
    reddit = Reddit(config.data_location)
    subreddits = list(subreddits)

    if subreddit_list is not None: 
        subreddits.extend([forum.strip().split("/")[-1] for forum in subreddit_list])

    for subreddit in subreddits:
        subr = reddit.get_subreddit(subreddit)
        top_authors = subr.top_authors(top_n)

        for auth in top_authors: print(subreddit + "," + auth)

if __name__ == '__main__':
    main()
