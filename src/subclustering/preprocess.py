import os
import json
from datetime import date
from functools import partial

import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from pathlib import Path

from reddit import Reddit
from utils.get_authors_timeline import get_authors_timeline, TopicsDFCache
import config


tqdm.pandas()

pre_topics = ['FT1', 'FT3', 'FT6','FT8']
years = ['2009','2010','2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']


authors = list()
unique_authors = set()


for topic in pre_topics:
    df = TopicsDFCache.load(topic)
    authors += [set(df['Author'])]
    unique_authors |= set(df['Author'])

full_authors = list(sorted(unique_authors.intersection(*authors)))


def get_year_from_row(reddit, row):
    post_id = row['SeqId']
    timestamp = reddit.get_post(post_id)['created_utc']
    ts = date.fromtimestamp(timestamp)
    return ts.year


def get_year_month_from_row(reddit, row):
    post_id = row['SeqId']
    timestamp = reddit.get_post(post_id)['created_utc']
    ts = date.fromtimestamp(timestamp)
    return f'{ts.year}{ts.month}'


def process_topic(topic):
    reddit = Reddit(config.data_location)
    df = TopicsDFCache.load(topic)

    # Add Year column
    #df['Year'] = df.progress_apply(partial(get_year_from_row, reddit), axis=1)
    df['Year-Month'] = df.progress_apply(partial(get_year_month_from_row, reddit), axis=1)
    # min =df['Year'].min()
    # max =df['Year'].max()
    #
    # print(f'Year range from {min} to {max}')

    # Filter out unneeded authors
    df = df[df['Author'].isin(full_authors)]

    df.to_csv(os.path.join(config.topic_dir, f'{topic}-filtered-with_year_and_month.csv'))


with Pool() as pool:
    pool.map(process_topic, pre_topics)
