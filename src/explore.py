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
import time
import csv
import click



# @click.command()
# @click.option('-a', '--author', 'authors', type=str, multiple=True)
def main():
    reddit = Reddit(config.data_location)

    for user in reddit.get_users():
        with open(f'../tmp/{user.name}.csv', 'w') as fp:
            #csv_file = csv.writer(fp)
            #count = 0
            for post in user.posts:
                if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
                    #csv_file.writerow([post.get('id'), time.ctime(post['created_utc']), post.get('subreddit'), post.get('selftext').replace('\n', ' ')])
                    fp.write(post.get('selftext').replace('\n', ' '))
                    fp.write('\n')

if __name__ == '__main__':
    main()
