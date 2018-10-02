"""
Xinru Yan
Sep 2018

This program generates a human readable file per user for results from top_user_posts.py
Data location:
    ../tmp/

Usage:
    python explore.py

"""
from reddit import Reddit
import config
import click



# @click.command()
# @click.option('-a', '--author', 'authors', type=str, multiple=True)
def main():
    reddit = Reddit(config.data_location)

    for user in reddit.get_users():
        with open(f'../tmp/{user.name}.txt', 'w') as fp:
            count = 0
            for post in user.posts:
                if 'title' and 'selftext' in post:
                    count += 1
                    fp.write(post['subreddit'] + '\n')
                    fp.write(post['title'] + '\n')
                    fp.write(post['selftext'].replace('\n', ' ') + '\n')
                    fp.write('\n\n')
            fp.write(str(count))


if __name__ == '__main__':
    main()
