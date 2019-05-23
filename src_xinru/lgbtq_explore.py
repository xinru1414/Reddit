"""
Xinru Yan
Feb 2019

Given program is for exploring the LGBTQ data

Usage:
   python lgbtq_explore.py --subreddit-list forums.txt
"""
from reddit import Reddit
import csv
import config
import click
import re
import string
import time
from datetime import date
from crawl_reddit import pull_posts
from collections import Counter
from collections import defaultdict
from datetime import datetime

exclude = set(string.punctuation)

def clean(text):
    # get rid of emojis
    #text = p.clean(text)
    # get rid of links
    text = re.sub(r'\(http\S+\)|http\S+|www.\S+|imgur.\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'•','',text,flags=re.MULTILINE)
    text = re.sub(r'\[|\]', '', text, flags=re.MULTILINE)
    # get rid of puncs
    text = ''.join(w for w in text if w not in exclude)
    text = re.sub(r'\s+', ' ', text, flags=re.MULTILINE)
    return text

def match(l:list, s:string):
    m = []
    for item in l:
        if item in s:
            m.append(item)
    return m

@click.command()
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
@click.option('-K', '--keyword-list', 'keyword_list', type=click.File("r"))
@click.option('-T', '--topic-list', 'topic_list', type=click.File("r"))
#@click.option('-O', '--output-file', 'output_file', default="user_activity.csv", type=click.File("w"))

def main(subreddit_list, keyword_list, topic_list):
    reddit = Reddit(config.data_location)
    subreddits = {subredit.strip().split("/")[-1] for subredit in subreddit_list}

    keywords = {keyword.strip().lower() for keyword in keyword_list}
    print(keywords)
    topics = {topic.strip().lower() for topic in topic_list}
    print(topics)

    for subreddit in subreddits:
        sub = reddit.get_subreddit(subreddit)
        with open(f'../lgbtq/data/{subreddit}.csv', 'w') as fp:
            csv_file = csv.writer(fp)
            csv_file.writerow(['PostId', 'PostTime', 'author', 'PostContent', 'MatchingWord', 'MatchTopic'])
            for post in sub.posts:
                if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]' and post['author'] != '[deleted]' and post['author'] != 'AutoModerator':
                    content_post = post.get('selftext').replace('\n', ' ').lower()
                    clean_text = clean(content_post)
                    match_1 = match(keywords,clean_text)
                    match_2 = match(topics,clean_text)

                    if len(set(match_1)) != 0 or len(set(match_2)) != 0:
                        csv_file.writerow([post.get('id'), time.ctime(post.get('created_utc')), post['author'], clean_text, set(match_1) if len(match_1) > 0 else None, set(match_2) if len(match_2) > 0 else None])
                    # content_post = nltk.tokenize.sent_tokenize(content_post)
                    # if len(content_post) > 4:
                    #     count = 0
                    #     for sent in content_post:
                    #         sent = clean(sent)
                    #         sent = nltk.tokenize.word_tokenize(sent)
                    #         sent = ' '.join(sent)
                    #         csv_file.writerow([post.get('id'), count, post['author'], sent])
                    #         count += 1

if __name__ == '__main__':
    main()











