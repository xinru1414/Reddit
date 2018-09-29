import praw
from psaw import PushshiftAPI
import pandas as pd
import datetime
import sys
import json
import os
from tqdm import tqdm
import click
import config


reddit = praw.Reddit(client_id = config.client_id,
					 client_secret = config.client_secret,
					 user_agent = config.user_agent,
					 user_name = config.user_name,
					 password = config.password)

# subreddit = reddit.subreddit(sys.argv[1])
# params = {'sort':'new', 'limit':None, 'syntax':'cloudsearch'}

api = PushshiftAPI()


# def do_search(begin_time):
# 	return subreddit.search('timestamp:{0}..{1}'.format(int((time_now - datetime.timedelta(days=365)).timestamp()),int(time_now.timestamp())),**params)


# def find_posts(subreddit):
# 	time_now = datetime.datetime.now()
# 	print(time_now)
# 	posts = []
# 	for n in range(5):
# 		for submission in do_search(time_now):
# 			posts.append(submission.selftext)
# 			print(submission.selftext)
# 			time_now = submission.created_utc
# 			print(time_now)
# 			n -= 1
# 	return posts


def find_posts(start, limit):
	return api.search_submissions(author='spd158', sort='asc', sort_type='created_utc', after=start, limit=limit)


def grab_more_posts(limit, db_filepath='spd158.json'):
	# Load posts we already have if we have any
	data = {'posts': {},
	        'newest_time': 0}
	if os.path.exists(db_filepath):
		with open(db_filepath, 'r') as fp:
			data = json.load(fp)
	posts = data['posts']
	newest_time = data['newest_time']

	# get some more and add them to the list/dict of posts we already have
	for post in tqdm(find_posts(newest_time, limit), total=limit):
		posts[post.id] = post.d_
		if post.created_utc > newest_time:
			newest_time = post.created_utc
	

	# Save all the posts
	data['posts'] = posts
	data['newest_time'] = newest_time
	with open(db_filepath, 'w') as fp:
		json.dump(data, fp)

@click.command()
@click.argument('limit', type=int, default=1000)
def main(limit):
	grab_more_posts(limit)
	# find_posts(subreddit)

if __name__ == '__main__':
	main()
		

#+MakeupAddiction+AustralianMakeup+PaleMUA+AisanBeauty+MakeupAddictionCanada+Makeup+MUAontheCheap+MakeupAddicts+BeautyGuruChatter+HighEndMakeup

#personal = subreddit.search('flair:Personal')

# topics_dict = { 'user':[],
# 				'title':[], 
#                 'upvote_ratio':[], 
#                 'comms_num': [], 
#                 'body':[]} 
#                 #'comments':[]}

# for submission in subreddit.search('Estee Lauder', sort='new', limit=None, syntax='cloudsearch'):
# 	topics_dict['user'].append(submission.author)
# 	topics_dict['title'].append(submission.title)
# 	topics_dict['upvote_ratio'].append(submission.upvote_ratio)
# 	topics_dict['comms_num'].append(submission.num_comments)
# 	topics_dict['body'].append(submission.selftext)
# 	print(submission.selftext.replace('\n', ' '))
# 	#topics_dict['comments'].append([comment.body for comment in submission.comments])

# topics_data = pd.DataFrame(topics_dict)
# topics_data.to_csv('MakeupAddictionTry.csv', index=False) 



