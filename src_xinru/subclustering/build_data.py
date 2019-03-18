import os
import json
from collections import defaultdict
from enum import Enum, auto

import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition

from tqdm import tqdm
import config
import numpy as np
import pandas as pd
from pathlib import Path


class SELECTION_STRAT(Enum):
    PICK_FIRST = auto()
    SUM = auto()
    MEAN = auto()


class TOPICS(Enum):
    ONE = auto()
    ALL = auto()


time_unit_column = 'Year-Month'


def au_to_texts(df):
    authors_to_texts = defaultdict(list)

    groups = df.groupby(['Author']).groups

    for group, rows in tqdm(groups.items(), desc='   Dataset Au', leave=False):
        for row in groups[group]:
            authors_to_texts[group] += [(df.iloc[row]['Text'], df.iloc[row][time_unit_column])]
    return authors_to_texts


def select_first(x):
    return x[0]


def get_topic_author_texts(table, topic):
    return {author: tuple(map(select_first, table[topic][author])) for author in table[topic].keys()}


def get_topic_author_text_years(table, topic):
    return {author: tuple(table[topic][author]) for author in table[topic].keys()}


TOPIC_DOC_CACHE = {}
def topic_per_doc(table, topic_name: str):
    global TOPIC_DOC_CACHE
    if topic_name not in TOPIC_DOC_CACHE:
        print('\tdoc')
        user_docs = []
        for k, v in get_topic_author_text_years(table, topic_name).items():
            user_docs.append((k, v))
        TOPIC_DOC_CACHE[topic_name] = tuple(sorted(user_docs))
    return TOPIC_DOC_CACHE[topic_name]


PCA_CACHE = {}
def pca_docs(docs: tuple, num_of_pcs=5):
    global PCA_CACHE
    print('\tpca')
    inputs = hash(docs) + hash(num_of_pcs)
    cache_path = Path(f'/usr2/Reddit/data_cache/pca_{inputs}.pkl')
    if not cache_path.exists():
        vec = CountVectorizer()
        rows_for_user = defaultdict(list)
        rows_for_year = defaultdict(list)
        text = []
        for item in docs:
            user, d = item
            for x, year in d:
                rows_for_user[user] += [len(text)]
                rows_for_year[year] += [len(text)]
                text += [x]
        print('\t\tvec transform')
        X = vec.fit_transform(text)

        print('\t\tDT')
        DT = pd.DataFrame(X.toarray(), columns=vec.get_feature_names())

        pca = decomposition.PCA(n_components=num_of_pcs)

        print('\t\tpca transform')
        DTtrans = pca.fit_transform(DT)
        print('\t\tpca transform done :)')

        # np.set_printoptions(precision=2, suppress=True)

        mapping = DTtrans, rows_for_user, rows_for_year
        # print(pca.explained_variance_ratio_)
        with open(cache_path, 'wb') as fp:
            pickle.dump(mapping, fp)
        return mapping
    else:
        with open(cache_path, 'rb') as fp:
            return pickle.load(fp)


def topic_author_vec(mapping, strat=SELECTION_STRAT.MEAN, year=None, num_of_pcs=5):
    pc, rows_for_user, rows_for_year = mapping
    vec = defaultdict(list)
    print('\tvec')
    for user, rows in rows_for_user.items():
        if year:
            rows = list(set(rows_for_year[year]).intersection(set(rows)))
        if not rows:
            vec[user] = np.array([np.nan for _ in range(num_of_pcs)])
        else:
            if strat == SELECTION_STRAT.MEAN:
                vec[user] = np.mean(pc[np.array(rows)], axis=0)
            elif strat == SELECTION_STRAT.SUM:
                vec[user] = np.sum(pc[np.array(rows)], axis=0)
            elif strat == SELECTION_STRAT.PICK_FIRST:
                vec[user] = pc[np.array(rows[0])]
    return vec


GET_DF_CACHE = {}


def get_topics(full_authors, table, topics: list, num_of_pcs=5, strat=SELECTION_STRAT.MEAN):
    all_topics = []
    for topic in tqdm(topics, desc='Getting topics'):
        mapping = pca_docs(topic_per_doc(table, topic), num_of_pcs)
        user_vec = topic_author_vec(mapping, strat)
        this_topic = []
        for author in full_authors:
            this_topic += [user_vec[author]]
        all_topics.append(this_topic)
    return all_topics


def get_df(dfs, full_authors, table, selection_stat, topic_selection, num_of_pcs):
    inputs = (selection_stat, topic_selection, num_of_pcs)
    if inputs not in GET_DF_CACHE:
        topics = dfs.keys()
        if topic_selection == TOPICS.ONE:
            topics = next(iter(dfs.keys()))
        topic_dfs = get_topics(full_authors, table, topics, num_of_pcs=num_of_pcs, strat=selection_stat)

        GET_DF_CACHE[inputs] = np.concatenate(topic_dfs, axis=1)
    return GET_DF_CACHE[inputs]


def get_all_df_and_per_year(topics, full_authors, years, table, selection_stat, num_of_pcs):
    years = years + ['all']
    all_topics = {year: [] for year in years}
    for topic in tqdm(topics, desc='Getting topics'):
        mapping = pca_docs(topic_per_doc(table, topic), num_of_pcs)

        for year in tqdm(years, desc='\tprocessing year', leave=False):
            if year == 'all':
                user_vecs = topic_author_vec(mapping, selection_stat)
            else:
                user_vecs = topic_author_vec(mapping, selection_stat, year=int(year), num_of_pcs=num_of_pcs)
            this_topic = []
            for author in full_authors:
                this_topic += [user_vecs[author]]
            all_topics[year].append(this_topic)

    year_dfs = {}
    for year in years:
        year_dfs[year] = np.concatenate(all_topics[year], axis=1)

    return year_dfs


class Cache:
    def __init__(self, cache_loc):
        self.cache_loc = cache_loc

    def load(self, *args, **kargs):
        if self.cache_loc.exists():
            with open(self.cache_loc, 'rb') as fp:
                return pickle.load(fp)
        else:
            data = self.create(*args, **kargs)
            with open(self.cache_loc, 'wb') as fp:
                pickle.dump(data, fp)
            return data


class DatasetCache(Cache):
    def __init__(self, name):
        super().__init__(Path(f'/usr2/Reddit/data_cache/dataset_{name}.pickle'))

    def create(self, dfs):
        dataset = {}
        for topic, df in tqdm(dfs.items(), desc='Building dataset'):
            dataset[topic] = au_to_texts(df)
        return dataset


class TableCache(Cache):
    def __init__(self, name):
        super().__init__(Path(f'/usr2/Reddit/data_cache/table_{name}.pickle'))

    def create(self, dataset, full_authors):
        table = {}
        for topic in dataset.keys():
            table[topic] = {}

        for author in tqdm(full_authors, desc='Building table'):
            for topic, ds in dataset.items():
                table[topic][author] = ds[author]
        return table


def main():
    topics = ['FT1', 'FT3', 'FT6','FT8']
    years = ['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    months = [f'{year}{m+1}' for year in years for m in range(12)]

    dfs = {}
    for topic_name in tqdm(topics, desc='Creating dfs'):
        topic_path = os.path.join(config.topic_dir, f'{topic_name}-filtered-with_year_and_month.csv')
        dfs[topic_name] = pd.read_csv(topic_path)

    dataset = DatasetCache('all').load(dfs)

    authors = list()
    unique_authors = set()
    for ds in dataset.values():
        authors += [set(ds.keys())]
        unique_authors |= set(ds.keys())

    full_authors = list(sorted(unique_authors.intersection(*authors)))
    with open(Path(f'/usr2/Reddit/data_local/full_authors3.json'), 'w') as fp:
        json.dump(full_authors, fp)
    print(f'Good Authors: {len(full_authors)}/{len(unique_authors)}')

    table = TableCache('all').load(dataset, full_authors)

    mean_allt_5_dict = get_all_df_and_per_year(dfs.keys(), full_authors, years=months, table=table, selection_stat=SELECTION_STRAT.MEAN, num_of_pcs=5)
    for month in months + ['all']:
        with open(Path(f'/usr2/Reddit/data_local/mean_allt_2_{month}.npy'), 'wb') as fp:
            np.save(fp, mean_allt_5_dict[month])


if __name__ == '__main__':
    main()

