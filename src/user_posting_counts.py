"""
Chris Bogart
Feb 2019

Summarize posting histories for a list of users, over a list of forums
The user list should be a list of users OR a list of forum,user.  The forum
column in the user list will be ignored though; 
we count all postings by each unique user, across any of the forums in the forum list.

Usage:
   python user_posting_counts.py --subreddit-list forums.txt --user-list users.txt --output_file user_activity.csv
"""
from reddit import Reddit
import csv
import config
import click
from crawl_reddit import pull_posts
from collections import Counter
from collections import defaultdict
from datetime import datetime


@click.command()
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
@click.option('-U', '--user-list', 'user_list', type=click.File("r"))
@click.option('-O', '--output-file', 'output_file', default="user_activity.csv", type=click.File("w"))
def main(user_list, subreddit_list, output_file):
    reddit = Reddit(config.data_location)
    subreddits = {forum.strip().split("/")[-1] for forum in subreddit_list}
    users = {useritem.strip().split(",")[-1] for useritem in user_list}
    subreddits -= set("")
    subreddits = sorted(subreddits)
    users -= set("")
    users = sorted(users)
    csvf = csv.writer(output_file)
    csvf.writerow(["username","month","subreddit","count"])

    for user in users:
        subcount = { s:defaultdict(int) for s in subreddits }
        for post in reddit.get_user(user).posts:
            if post.get("subreddit","") in subreddits:
                utc = datetime.utcfromtimestamp(post["created_utc"]).strftime('%Y-%m')
                subcount[post.get("subreddit","")][utc] += 1
        for s in sorted(subcount):
            for t in sorted(subcount[s]):
                csvf.writerow([user,t,s,subcount[s][t]])
            
if __name__ == '__main__':
    main()
