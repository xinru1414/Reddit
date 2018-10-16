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
import os
import time
import csv
import click



# @click.command()
# @click.option('-a', '--author', 'authors', type=str, multiple=True)
def main():
    reddit = Reddit(config.data_location)
    # following code explores saving user posts per user
    # for user in reddit.get_users():
    #     os.mkdir('../tmp/{user.name}')
    #     #with open(f'../tmp/{user.name}.csv', 'w') as fp:
    #         #csv_file = csv.writer(fp)
    #         #count = 0
    #         for post in user.posts:
    #             with open(f'../tmp/{user.name}.csv', 'w') as fp:
    #             if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
    #                 #csv_file.writerow([post.get('id'), time.ctime(post['created_utc']), post.get('subreddit'), post.get('selftext').replace('\n', ' ')])
    #                 fp.write(post.get('selftext').replace('\n', ' '))
    #                 fp.write('\n')
    # following code explores saving user posts per user per post
    # for user in reddit.get_users():
    #     dirpath = '../user_posts/'+user.name
    #     os.mkdir(dirpath)
    #     for post in user.posts:
    #         if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
    #             filepath = os.path.join(dirpath, post.get('id')+'.txt')
    #             with open(filepath, 'w') as fp:
    #                 fp.write(post.get('selftext').replace('\n',' '))

    # following code save all user posts into one file
    # with open (f'../all_posts/all.txt', 'w') as fp:
    #     for user in reddit.get_users():
    #         print('Processing ' + str(user.name) + ' \'s history')
    #         for post in user.posts:
    #             if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
    #                 fp.write(post.get('selftext').replace('\n', ' '))
    #                 fp.write('\n')
    # the following code saves a text file per user
    for user in reddit.get_users():
        with open(f'../user_history/{user.name}.txt', 'w') as fp:
            for post in user.posts:
                if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
                    fp.write(post.get('selftext').replace('\n',' '))
                    fp.write('\n')


if __name__ == '__main__':
    main()
