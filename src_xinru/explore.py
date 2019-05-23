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
import re
import config
import nltk
import os
import time
import csv
import click



# @click.command()
# @click.option('-a', '--author', 'authors', type=str, multiple=True)
def main():
    reddit = Reddit(config.data_location)

    # following code explores saving user posts per user
    for user in reddit.get_users():
        #os.mkdir('../tmp/{user.name}')
        with open(f'../tmp/{user.name}.csv', 'w') as fp:
            csv_file = csv.writer(fp)
            csv_file.writerow(['SeqId','InstNo','Author','Text'])
            for post in user.posts:
            #with open(f'../tmp/{user.name}.csv', 'w') as fp:
                if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]' and post['subreddit'] != 'makeupexchange':
                    content_post = post.get('selftext').replace('\n', ' ')
                    content_post = re.sub(r'\[.*?\]\(http\S+\)|http\S+', '', content_post, flags=re.MULTILINE)
                    content_post = nltk.tokenize.word_tokenize(content_post)
                    content_post = ' '.join(content_post)
                    content_post = nltk.tokenize.sent_tokenize(content_post)
                    for i in range(len(content_post) -1):
                        content_post[i] = content_post[i]+' <SENT>'
                    content_post = ' '.join(content_post)
                    csv_file.writerow([post.get('id'), 0, user.name, content_post])
    # following code explores saving user posts per user per post
    # for user in reddit.get_users():
    #     dirpath = '../user_posts/'+user.name
    #     os.mkdir(dirpath)
    #     for post in user.posts:
    #         if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]':
    #             filepath = os.path.join(dirpath, post.get('id')+'.txt')
    #             with open(filepath, 'w') as fp:
    #                 fp.write(post.get('selftext').replace('\n',' '))

    #following code save all user posts into one file
    # with open (f'../all_posts/all.txt', 'w') as fp:
    #     for user in reddit.get_users():
    #         print('Processing ' + str(user.name) + ' \'s history')
    #         posts = []
    #         for post in user.posts:
    #             if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]'and post['subreddit'] != 'makeupexchange':
    #                 if post.get('selftext') not in posts:
    #                     fp.write(post.get('selftext').replace('\n', ' '))
    #                     fp.write('\n')
    #                     posts.append(post.get('selftext'))
    #following code saves a text file per user
    # for user in reddit.get_users():
    #     with open(f'../test_user_history/{user.name}.txt', 'w') as fp:
    #         posts = []
    #         for post in user.posts:
    #             if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]' and post['subreddit'] != 'makeupexchange':
    #                 if post.get('selftext') not in posts:
    #                     content_post = post.get('selftext').replace('\n', ' ')
    #                     content_post = re.sub(r'\[.*?\]\(http\S+\)|http\S+', '', content_post, flags=re.MULTILINE)
    #                     fp.write(content_post)
    #                     fp.write('\n\n')
    #                     posts.append(post.get('selftext'))

if __name__ == '__main__':
    main()
