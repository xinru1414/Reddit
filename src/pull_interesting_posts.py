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

    # for subreddit in subreddits:
    subr = reddit.get_subreddit(subreddit)
    users = Counter(post['author'] for post in subr.posts)
    del users['[deleted]']
    top_authors = next(zip(*users.most_common(top_n)))

    print('Pulling the following authors...')
    print('\n'.join(top_authors))

    pull_posts(1000, authors=top_authors)


if __name__ == '__main__':
    main()
