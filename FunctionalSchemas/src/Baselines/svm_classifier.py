import argparse
import numpy as np
from dataset_loader import DatasetLoader
from sklearn.svm import SVC
from joblib import dump, load

def create_unigram_vectors(data, vocab):
    #create bag of unigram vectors
    vectors = np.zeros((len(data), len(vocab.keys())))
    for i, instance in enumerate(data):
        vectors[i][instance[1]] = 1
    return vectors

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--train_data', type=str, action='store')
    parser.add_argument('--dev_data', type=str, action='store')
    parser.add_argument('--test_data', type=str, action='store')
    parser.add_argument('--model_path', type=str, action='store')
    parser.add_argument('--vocab_path', type=str, action='store')
    parser.add_argument('--do_train', action='store_true', default=False)
    parser.add_argument('--do_eval', action='store_true', default=False)
    parser.add_argument('--use_bigrams', action='store_true', default=False)
    args = parser.parse_args()

    dataset = DatasetLoader(args.train_data, args.dev_data, args.test_data)
    print('Dataset Loaded...')
    train_vectors = create_unigram_vectors(dataset.train_data, dataset.word_vocab)
    dev_vectors = create_unigram_vectors(dataset.dev_data, dataset.word_vocab)
    test_vectors = create_unigram_vectors(dataset.test_data, dataset.word_vocab)
    print('Vector Creation Complete...')

    train_labels = np.array([x[-1] for x in dataset.train_data])
    dev_labels = np.array([x[-1] for x in dataset.dev_data])
    test_labels = np.array([x[-1] for x in dataset.test_data])

    if args.do_train:
        classifier = SVC(C=0.1, kernel='linear')
        classifier.fit(train_vectors, train_labels)
        dump(classifier, args.model_path)
        print('Model Training Complete...')
    if args.do_eval:
        classifier = load(args.model_path)
        print('Accuracy on Test Set: {}'.format(classifier.score(test_vectors, test_labels)))
