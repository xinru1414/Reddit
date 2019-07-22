from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score
from dataset_loader import DatasetLoader
from sklearn.externals import joblib
import numpy as np
from tqdm import tqdm
import click
from collections import Counter
import pandas as pd
import math


def get_labels(dataset: list):
    labels = []
    for item in dataset:
        labels.append(item[1])
    return labels


def get_vocab(dataset: list, cutoff: int):
    corpus = []
    for item in dataset:
        for sent in item[3]:
            corpus.extend(sent[0])
    corpus = Counter(corpus)
    vocab = corpus.most_common(cutoff)
    vocab = [i[0] for i in vocab]
    return vocab


def preprocess(dataset: list, schemas: list, mapping: list):
    '''

    :param dataset: dataset, movie or reddit
    :param schemas: a list of schemas
    :return:
    '''
    schema_data = []
    nonschema_data = []
    for item in dataset:
        example = [[] for i in range(3)]
        example_nonschema = [[] for i in range(3)]
        if item[2] in mapping:
            j = 0
            schema = schemas[j]
        else:
            j = 1
            schema = schemas[j]
        schema_sents = []
        non_schema_sents = []
        all_sents = []
        for sent in item[3]:
            if sent[1] in schema:
                schema_sents.extend(sent[0])
            else:
                non_schema_sents.extend(sent[0])
            all_sents.extend(sent[0])
        example[2] = all_sents
        example[j] = schema_sents
        example_nonschema[2] = all_sents
        schema_data.append(example)
        nonschema_data.append(example_nonschema)
    assert len(dataset) == len(schema_data)
    assert len(schema_data) == len(nonschema_data)
    return schema_data, nonschema_data


def bow(data: list, vocab: list):
    '''

    :param data:
    :param vocab:
    :return:
    '''
    bow = []
    for sents in tqdm(data):
        bag_vectors = []
        for i, sent in enumerate(sents):
            bag_vector = np.zeros(len(vocab))
            for word in sent:
                for i, w in enumerate(vocab):
                    if word == w:
                        bag_vector[i] += 1
            bag_vectors.append(bag_vector)
        bow.append(bag_vectors)
    array = np.array(bow).reshape((len(bow), (3*len(vocab))))
    print(array.shape)
    return array


def computeTFDict(data: list):
    """ Returns a tf dictionary for each review whose keys are all
    the unique words in the review and whose values are their
    corresponding tf.
    """
    #Counts the number of times the word appears in review
    TFDict = []
    for sents in data:
        TFDicts = []
        for sent in sents:
            TF = {}
            for word in sent:
                if word in TFDict:
                    TF[word] += 1
                else:
                    TF[word] = 1
            for word in TF:
                TF[word] = TF[word] / len(sent)
            TFDicts.append(TF)
        TFDict.append(TFDicts)
    return TFDict


def computeCountDict(data: list):
    """ Returns a dictionary whose keys are all the unique words in
    the dataset and whose values count the number of reviews in which
    the word appears.
    """
    # Run through each review's tf dictionary and increment countDict's (word, doc) pair
    countDict = {}
    for sents in data:
        for sent in sents:
            for word in sent:
                if word in countDict:
                    countDict[word] += 1
                else:
                    countDict[word] = 1
    return countDict


def computeIDFDict(data: list, d: dict):
    """ Returns a dictionary whose keys are all the unique words in the
    dataset and whose values are their corresponding idf.
    """
    idfDict = {}
    for word in d:
        idfDict[word] = math.log(len(data) / d[word])
    return idfDict


def computeTFIDFDict(data, idfDict):
    """ Returns a dictionary whose keys are all the unique words in the
    review and whose values are their corresponding tfidf.
    """
    TFIDF = []
    for sents in data:
        tfidf = []
        for TFDict in sents:
            TFIDFDict = {}
            for word in TFDict:
                TFIDFDict[word] = TFDict[word] * idfDict[word]
            tfidf.append(TFIDFDict)
        TFIDF.append(tfidf)
    return TFIDF


def tfidfVector(data: list, vocab: list):
    '''

    :param data:
    :return:
    '''
    V = []
    for sents in tqdm(data):
        vectors = []
        for i, sent in enumerate(sents):
            vector = np.zeros(len(vocab))
            for word in sent:
                for i, w in enumerate(vocab):
                    if word == w:
                        vector[i] = sent[word]
            vectors.append(vector)
        V.append(vectors)
    array = np.array(V).reshape((len(V), (3 * len(vocab))))
    return array


def tfidf(data: list, vocab: list):
    tfDict = computeTFDict(data)
    countDict = computeCountDict(data)
    idfDict = computeIDFDict(data, countDict)
    tfIDF = computeTFIDFDict(tfDict, idfDict)
    vectors = tfidfVector(tfIDF, vocab)
    return vectors


def matrix(y_true, y_pred):
    y_true = pd.Series(y_true)
    y_pred = pd.Series(y_pred)
    matrix = pd.crosstab(y_true, y_pred, rownames=['True'], colnames=['Predicted'], margins=True)
    return matrix


def train_model(mode: str, train: str, dev: str, test: str, model_path: str, schemas: list, tech: str, mapping: list):
    print(f'using {tech} to create features')
    print('loading data')
    dataloader = DatasetLoader(train, dev, test)
    vocab = get_vocab(dataloader.train_data, 15000)
    print(f'vocab size {len(vocab)}')

    # if tech == 'bow':
    #     classifier = MultinomialNB()
    # else:
    #     classifier = GaussianNB()
    #classifier = LogisticRegression(random_state=0, solver='lbfgs', multi_class='multinomial', max_iter=2000, class_weight='balanced')
    classifier = SVC(C=0.1, kernel='linear')
    print(mode)
    print('creating training vectors')
    if mode == 'schema':
        if tech == 'bow':
            train_vectors = bow(preprocess(dataloader.train_data, schemas, mapping)[0], vocab)
            test_vectors = bow(preprocess(dataloader.test_data, schemas, mapping)[0], vocab)
        else:
            train_vectors = tfidf(preprocess(dataloader.train_data, schemas, mapping)[0], vocab)
            test_vectors = tfidf(preprocess(dataloader.test_data, schemas, mapping)[0], vocab)
    else:
        if tech == 'bow':
            train_vectors = bow(preprocess(dataloader.train_data, schemas, mapping)[1], vocab)
            test_vectors = bow(preprocess(dataloader.test_data, schemas, mapping)[1], vocab)
        else:
            train_vectors = tfidf(preprocess(dataloader.train_data, schemas, mapping)[1], vocab)
            test_vectors = tfidf(preprocess(dataloader.test_data, schemas, mapping)[1], vocab)

    train_labels = get_labels(dataloader.train_data)

    print('training the model')
    print(f'{train_vectors.shape}')
    model = classifier.fit(train_vectors, train_labels)

    print('creating testing vectors and testing model')
    test_pred = model.predict(test_vectors)
    test_true = get_labels(dataloader.test_data)
    print(classification_report(test_true, test_pred))
    print(accuracy_score(test_true, test_pred))
    cm = matrix(test_true, test_pred)
    print(f'confusion matrix \n {cm} \n')

    print('saving the model')
    joblib.dump(model, model_path)


@click.command()
@click.option('-m', '--mode', 'mode', type=str)
@click.option('-d', '--data', 'data', type=str)
@click.option('-t', '--tech', 'tech', type=str)
def main(mode, data, tech):
    root_dir = '../data/'
    train = '/train_with_schema.jsonl'
    dev = '/dev_with_schema.jsonl'
    test = '/test_with_schema.jsonl'

    train_path = root_dir + data + train
    dev_path = root_dir + data + dev
    test_path = root_dir + data + test
    model_path = f'../model/{data}/model5_{mode}_{tech}_NB.pkl'

    if data == 'movies':
        schemas = [[0, 1, 4], [1, 2, 6, 8], [1, 3, 4, 5, 9], [2, 3, 6], [5, 6]]
        mapping = [0, 1]
    else:
        schemas = [[3, 4, 5, 7], [7, 9, 2, 6], [3, 4, 5, 9], [3, 4, 9], [0, 2, 3]]
        mapping = [0, 2, 3]

    train_model(mode=mode, train=train_path, dev=dev_path, test=test_path, model_path=model_path, schemas=schemas, tech=tech, mapping=mapping)


if __name__ == "__main__":
    main()