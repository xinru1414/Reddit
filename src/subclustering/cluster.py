from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import json
from sklearn.cluster import KMeans
from build_data import TableCache


def get_author_topic_texts(table, topics, author):
    return {topic: set(table[topic][author]) for topic in topics}


def clusters_to_pattern(years: List[str], clusters: Dict[str, int]):
    return tuple([clusters[x] for x in years if clusters.get(x, None) is not None])


def get_group(groups, author):
    for group, authors in enumerate(groups):
        if author in authors:
            return group
    return 'non'


if __name__ == '__main__':
    topics = ['FT1', 'FT3', 'FT6', 'FT8']
    # #years = ['2009','2010','2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018','2019']
    #
    # months = ['20171', '20172']

    years = ['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
    months = [f'{year}{m+1}' for year in years for m in range(12)]

    mean_allt_5_dict = {}
    for month in months + ['all']:
        with open(Path(f'/usr2/Reddit/data_local/mean_allt_2_{month}.npy'), 'rb') as fp:
            mean_allt_5_dict[month] = np.load(fp)

    with open(Path('/usr2/Reddit/data_local/full_authors3.json'), 'r') as fp:
        full_authors = json.load(fp)

    table = TableCache('all').load()

    km = KMeans(n_clusters=3).fit(mean_allt_5_dict['all'])

    # TODO: What does this do?
    ppl = []
    for cluster in [0, 1, 2]:
        print(f'Cluster: {cluster}')
        d = km.transform(mean_allt_5_dict['all'])[:, cluster]
        ind = np.argsort(d)[::][:3]
        print(f'Closest {3} Author IDs: {ind}')
        for item in ind:
            ppl.append(full_authors[item])
    with open(Path('/usr2/Reddit/data/core_user.txt'), 'w') as file:
        for item in ppl:
            file.write(item+'\n')
    print(ppl)

    groups = [[], [], []]
    for index, item in enumerate(km.labels_):
        groups[item].append(full_authors[index])

    author_clusters = {}

    for i, author in enumerate(full_authors):
        author_clusters[author] = {'all': int(km.predict(mean_allt_5_dict['all'][i].reshape(1, -1)))}
        for month in months:
            if np.any(np.isnan(mean_allt_5_dict[month][i])):
                #author_clusters[author][month] = None
                pass
            else:
                author_clusters[author][month] = int(km.predict(mean_allt_5_dict[month][i].reshape(1, -1)))

    with open(Path('/usr2/Reddit/data_local/author_clusters.json'), 'w') as fp:
        json.dump(author_clusters, fp)

    # INCLUDE_SUBPATTERNS = False

    group_patterns = {x: [] for x in list(range(len(groups)))+['non']}
    group_patterns_to_authors = {x: defaultdict(list) for x in list(range(len(groups)))+['non']}
    # () means
    for author, clusters in author_clusters.items():
        pattern = clusters_to_pattern(months, clusters)
        group_patterns[get_group(groups, author)] += [pattern]
        group_patterns_to_authors[get_group(groups, author)][pattern] += [author]

    #print(group_patterns)
    group_pattern_counts = {}
    for group, patterns in group_patterns.items():
        group_pattern_counts[group] = Counter(patterns)

    for group, counts in group_pattern_counts.items():
        print(f'{group}: {counts}')
        print(sum(counts.values())-counts['non'])

    print('\n\n')
    print('group 0 most transition:\n\t',group_patterns_to_authors[0][(0, 0)])
    #print('group 0 second transition:\n\t', group_patterns_to_authors[0][(0, 1)])
    print('group 1 most transition:\n\t', group_patterns_to_authors[1][(1, 1)])
    #print('group 1 second transition:\n\t ', group_patterns_to_authors[1][(2, 0)])
    print('group 2 most transition:\n\t', group_patterns_to_authors[2][(2, 2)])
    #print('group 2 second transition:\n\t', group_patterns_to_authors[2][(1, 0)])
