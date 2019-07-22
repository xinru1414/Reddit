import csv
import json
import itertools
from collections import Counter
from nltk import word_tokenize


class DatasetLoader:
    """
    Common utitily class to load document classification datasets
    Performs basic preprocessing such as tokenization and lowercasing
    Also converts labels into integers
    """

    def __init__(self, train_path, dev_path, test_path):
        #call json file loader on all datasets
        raw_train_data = self.json_loader(train_path)
        raw_dev_data = self.json_loader(dev_path)
        raw_test_data = self.json_loader(test_path)

        #load stopword file
        input = open('Baselines/stopwords.txt')
        self.stopwords = []
        for line in input:
            self.stopwords.append(line.strip())
        self.stopwords = set(self.stopwords)

        #call vocab creator on labels
        labels = [x[1] for x in raw_dev_data]
        self.label_vocab = self.create_vocab(labels, cutoff=0)

        #call text preprocessor
        self.preprocess_text(raw_train_data, self.stopwords)
        self.preprocess_text(raw_dev_data, self.stopwords)
        self.preprocess_text(raw_test_data, self.stopwords)



        #convert all labels into integers
        self.create_sequences(raw_train_data, self.label_vocab)
        self.create_sequences(raw_dev_data, self.label_vocab)
        self.create_sequences(raw_test_data, self.label_vocab)

        self.train_data = raw_train_data
        self.dev_data = raw_dev_data
        self.test_data = raw_test_data

    def csv_loader(self, path):
        reader = csv.reader(open(path, 'r'), delimiter='\t', quotechar='"')
        next(reader, None)
        data = []
        for row in reader:
            data.append(row)
        return data

    def json_loader(self, path):
        reader = open(path, 'r')
        data = []
        for line in reader:
            data.append(json.loads(line))
        return data

    def create_vocab(self, words, unk=False, cutoff=10):
        counter = Counter()
        counter.update(words)
        filtered_counts = {k:v for k,v in counter.items() if v >= cutoff}
        words = list(filtered_counts.keys())
        if unk:
            words = ["<unk>"] + words
        vocab = dict(zip(words, range(len(words))))
        print(f'number of labels/vocabs {len(vocab.keys())}')
        return vocab

    def preprocess_text(self, data, stopwords):
        #Currently performs tokenization and lowercasing. Add more if needed
        for sample in data:
            for pair in sample[-1]:
                sentence, label = pair
                processed_sent = word_tokenize(sentence.strip())
                processed_sent = [x.lower() for x in processed_sent if x not in stopwords]
                pair[0] = processed_sent

    def create_sequences(self, dataset, label_vocab):
        for i, instance in enumerate(dataset):
            instance[1] = label_vocab[instance[1]]
