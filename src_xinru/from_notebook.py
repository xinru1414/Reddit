#!/usr/bin/env python
# coding: utf-8

import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter, OrderedDict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition
import matplotlib.pyplot as plt
from yellowbrick.cluster import KElbowVisualizer
from pandas.plotting import scatter_matrix as sm
import seaborn as sns
from enum import Enum, auto
from scipy.stats import ttest_ind
from itertools import combinations
from nltk import FreqDist
import nltk
from nltk.corpus import stopwords


nltk.download('stopwords')


class SELECTION_STRAT(Enum):
    PICK_FIRST = auto()
    SUM = auto()
    MEAN = auto()


class TOPICS(Enum):
    ONE = auto()
    ALL = auto()


root_dir = '/Users/xinruyan/Developer/Reddit/CSM-cosmetic_with_emoji-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.5-N0.9-SEQ/'

topics = OrderedDict([('Skin Situation', 'FT4.csv'),
                      ('Routine', 'FT0.csv'),
                      ('Reviews', 'FT6.csv'),
                      ('Outlook', 'FT8.csv')])

dfs = {}
for topic_name, topic_path in topics.items():
    dfs[topic_name] = pd.read_csv(root_dir + topic_path)


# In[51]:


def get_the_group(df):
    return df.groupby(['Author']).groups


# In[52]:


def au_to_texts(df):
    authors_to_texts = defaultdict(list)

    groups = get_the_group(df)

    for group, rows in groups.items():
        for row in groups[group]:
            authors_to_texts[group] += [df.iloc[row]['Text']]
    return authors_to_texts


dataset = {}

for topic, df in dfs.items():
    dataset[topic] = au_to_texts(df)

# In[54]:


authors = list()
unique_authors = set()
for ds in dataset.values():
    authors += [set(ds.keys())]
    unique_authors |= set(ds.keys())

print(f'Total authors: {len(unique_authors)}')
full_authors = list(unique_authors.intersection(*authors))
print(f'Good Authors: {len(full_authors)}')

# In[55]:


table = {}

for topic in dataset.keys():
    table[topic] = {}

for author in full_authors:
    for topic, ds in dataset.items():
        table[topic][author] = ds[author]


# In[56]:


def get_author_topic_texts(author):
    return {topic: set(table[topic][author]) for topic in topics.keys()}


# In[47]:


# with open("author_topic_text.txt", 'w') as fp:
#     for author in full_authors:
#         fp.write('User: ' + author + '\n')
#         for k, v in get_author_topic_texts(author).items():
#             fp.write(k + '\n')
#             for item in v:
#                 fp.write('\t' + item + '\n')
#         fp.write('\n')


# In[57]:


def get_topic_author_texts(topic):
    return {author: tuple(table[topic][author]) for author in table[topic].keys()}


# In[58]:


TOPIC_DOC_CACHE = {}


def topic_per_doc(topic_name: str):
    global TOPIC_DOC_CACHE
    if topic_name not in TOPIC_DOC_CACHE:
        user_docs = []
        for k, v in get_topic_author_texts(topic_name).items():
            user_docs.append((k, v))
        TOPIC_DOC_CACHE[topic_name] = tuple(user_docs)
    return TOPIC_DOC_CACHE[topic_name]


PCA_CACHE = {}


def pca_docs(docs: tuple, num_of_pcs=5):
    global PCA_CACHE
    inputs = hash(docs) + hash(num_of_pcs)
    if inputs not in PCA_CACHE:
        vec = CountVectorizer()
        rows_for_user = defaultdict(list)
        text = []
        for item in docs:
            user, d = item
            for x in d:
                rows_for_user[user] += [len(text)]
                text += [x]
        X = vec.fit_transform(text)

        DT = pd.DataFrame(X.toarray(), columns=vec.get_feature_names())

        pca = decomposition.PCA(n_components=num_of_pcs)

        DTtrans = pca.fit_transform(DT)

        np.set_printoptions(precision=2, suppress=True)

        mapping = DTtrans, rows_for_user
        # print(pca.explained_variance_ratio_)
        PCA_CACHE[inputs] = mapping
    return PCA_CACHE[inputs]


def topic_author_vec(mapping, strat=SELECTION_STRAT.MEAN):
    pc, rows_for_user = mapping
    vec = defaultdict(list)
    for user, rows in rows_for_user.items():
        if strat == SELECTION_STRAT.MEAN:
            vec[user] = np.mean(pc[np.array(rows)], axis=0)
        elif strat == SELECTION_STRAT.SUM:
            vec[user] = np.sum(pc[np.array(rows)], axis=0)
        elif strat == SELECTION_STRAT.PICK_FIRST:
            vec[user] = pc[np.array(rows[0])]
    return vec


def get_topics(topics: list, num_of_pcs=5, strat=SELECTION_STRAT.MEAN):
    all_topics = []
    for topic in topics:
        user_vec = topic_author_vec(pca_docs(topic_per_doc(topic), num_of_pcs), strat)
        this_topic = []
        for author in full_authors:
            this_topic += [user_vec[author]]
        all_topics.append(this_topic)
    return all_topics


# In[61]:


def doKmeans(X, nclust):
    model = KMeans(init='k-means++', algorithm='full', n_clusters=nclust)
    model.fit(X)
    clust_labels = model.predict(X)
    cent = model.cluster_centers_
    return (clust_labels, cent)


# In[62]:


# In[63]:


GET_DF_CACHE = {}


def get_df(selection_stat, topic_selection, num_of_pcs):
    inputs = (selection_stat, topic_selection, num_of_pcs)
    if inputs not in GET_DF_CACHE:
        topics = dfs.keys()
        if topic_selection == TOPICS.ONE:
            # topics = next(iter(dfs.keys()))
            # topics = ['Routine']
            topics = ['Skin Problems']
        topic_dfs = get_topics(topics, num_of_pcs=num_of_pcs, strat=selection_stat)

        GET_DF_CACHE[inputs] = np.concatenate(topic_dfs, axis=1)
    return GET_DF_CACHE[inputs]


# In[64]:


mean_allt_5 = get_df(SELECTION_STRAT.MEAN, TOPICS.ALL, 5)

# In[65]:


mean_allt_5.shape

# In[67]:


pvalue_threshold = 0.01


def calc_stats(df):
    stat_rows = []

    df_length = max(filter(lambda x: isinstance(x, int), df.columns)) + 1

    for i in range(df_length):
        good = True
        for a, b in combinations(['GroupOne', 'GroupTwo', 'GroupThree'], 2):
            stat, p = ttest_ind(df[df['Group'] == a][i], df[df['Group'] == b][i])
            # stat_rows += [(i, f'{a}-{b}', stat, p, p<pvalue_threshold)]
            if p >= pvalue_threshold:
                good = False
        stat_rows += [(i, stat, p, good)]
    stats = pd.DataFrame(stat_rows, columns=['Component', 't-stat', 'p-value', 'Ok?'])
    return stats


calc_stats(df2)


# In[68]:


def get_com_sorted(df, com_i):
    com = df.loc[:, [com_i]]
    mean = com.mean()
    com['dist'] = com.apply(lambda x: abs(x[com_i] - mean), axis=1)
    com['high'] = com.apply(lambda x: x[com_i] > mean, axis=1)
    return com.sort_values(by=['dist'])


def get_middle_samples(s_com, com_i, n_authors):
    topic = list(topics.keys())[com_i // 5]  # This assumes 5 PCs per topic
    samples = {}
    for author_i in s_com[com_i][:n_authors].index:
        author = full_authors[author_i]
        samples[author] = dataset[topic][author]
    return samples


def get_right_samples(s_com, com_i, n_authors):
    topic = list(topics.keys())[com_i // 5]  # This assumes 5 PCs per topic
    samples = {}
    for author_i in s_com[s_com['high']][com_i][-n_authors:].index:
        author = full_authors[author_i]
        samples[author] = dataset[topic][author]
    return samples


def get_left_samples(s_com, com_i, n_authors):
    topic = list(topics.keys())[com_i // 5]  # This assumes 5 PCs per topic
    samples = {}
    for author_i in s_com[s_com['high'] == False][com_i][-n_authors:].index:
        author = full_authors[author_i]
        samples[author] = dataset[topic][author]
    return samples


df2 = mean_allt_5
km = KMeans(n_clusters=3).fit(df2)

# In[292]:


ppl = []
for cluster in [0]:
    print(f'Cluster: {cluster}')
    d = km.transform(df2)[:, cluster]
    ind = np.argsort(d)[::][:50]
    print(f'Closest {50} Author IDs: {ind}')
    for item in ind:
        ppl.append(full_authors[item])
print(ppl)

# In[280]:


author_name = full_authors[7527]
author_name

# In[204]:


get_author_topic_texts(full_authors[5654])

# In[187]:


cluster_map = pd.DataFrame()
cluster_map['data_index'] = df2.index.values
cluster_map['cluster'] = km.labels_

# In[199]:


cluster_map[cluster_map.cluster == 2].shape

# In[290]:


pd.options.display.max_seq_items = 2000
full_authors
len(full_authors)

# In[324]:


groups = [[], [], []]

for index, item in enumerate(cluster_map['cluster']):
    groups[item].append(full_authors[index])
groups[0]
