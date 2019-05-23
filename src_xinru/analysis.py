
import pandas as pd
import numpy as np
from collections import defaultdict, Counter, OrderedDict
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import decomposition

root_dir = '../CSM-cosmetic_with_emoji-S5-FT10-BT5-FA0.1-BA1.0-B0.001-SG1.0-AG0.1-E0.5-N0.9-SEQ/'

topics = OrderedDict([('Skin Situation', 'FT4.csv'),
          ('Skin Problem', 'FT7.csv')])
dfs = {}
for topic_name, topic_path in topics.items():
    dfs[topic_name] = pd.read_csv(root_dir+topic_path)


def get_the_group(df):
    return df.groupby(['Author']).groups


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

authors = list()
unique_authors = set()
for ds in dataset.values():
    authors += [set(ds.keys())]
    unique_authors |= set(ds.keys())

print(f'Total authors: {len(unique_authors)}')
full_authors = list(unique_authors.intersection(*authors))
print(f'Good Authors: {len(full_authors)}')

table = {}

for topic in dataset.keys():
    table[topic] = {}

for author in full_authors:
    for topic, ds in dataset.items():
        table[topic][author] = ds[author]







def get_author_topic_texts(author):
    return {topic: set(table[topic][author]) for topic in topics.keys()}

def get_topic_author_texts(topic):
    return {author: tuple(table[topic][author]) for author in table[topic].keys()}

TOPIC_DOC_CACHE = {}
def topic_per_doc(topic_name:str):
    global TOPIC_DOC_CACHE
    if topic_name not in TOPIC_DOC_CACHE:
        user_docs = []
        for k,v in get_topic_author_texts(topic_name).items():
            user_docs.append((k, v))
        TOPIC_DOC_CACHE[topic_name] = tuple(user_docs)
    return TOPIC_DOC_CACHE[topic_name]

PCA_CACHE = {}
def pca_docs(docs:tuple, num_of_pcs=5):
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


        DT = pd.DataFrame(X.toarray(),columns=vec.get_feature_names())

        pca = decomposition.PCA(n_components=num_of_pcs)

        DTtrans = pca.fit_transform(DT)

        np.set_printoptions(precision=2,suppress=True)

        mapping = DTtrans, rows_for_user
        #print(pca.explained_variance_ratio_)
        PCA_CACHE[inputs] = mapping
    return PCA_CACHE[inputs]
