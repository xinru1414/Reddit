import sys
import os
import csv
import json

def read_ids_and_labels(file):
    next(file, None)
    data = []
    for row in file:
        data.append([row[0], row[-1]])
    return data

def read_text(file):
    next(file, None)
    data = {}
    for row in file:
        id = row[0]
        text = row[-1].strip()
        if id in data:
            data[id].append(text)
        else:
            data[id] = [text]
    return data

def read_topic_labels(text, file):
    next(file, None)
    data = {}
    for row in file:
        id = row[0]
        sent = int(row[1])
        sentence = text[id][sent]
        topic = int(row[-2])
        if id in data:
            data[id].append((sentence, topic))
        else:
            data[id] = [(sentence, topic)]
    return data

def read_pca_file(schemas, file):
    next(file, None)
    weights = {}
    for i, row in enumerate(file):
        if i == len(schemas):
            break
        weights[i] = [0.0]*10
        for topic in schemas[i]:
            weights[i][topic] = abs(float(row[topic+1]))
    return weights

def assign_schemas(metadata, topics, weights):
    data = []
    for sample in metadata:
        id, label = sample
        cur_text = topics[id]
        topic_prop = [0.0]*10
        total = 0.0
        for sentence in cur_text:
            total += 1
            topic_prop[sentence[1]] += 1
        topic_prop = [x/total for x in topic_prop]
        max_score = -10000
        max_schema = -1
        for schema in weights:
            score = sum([x*y for x,y in zip(topic_prop, weights[schema])])
            if score >= max_score:
                max_score = score
                max_schema = schema
        data.append([id,label,max_schema,cur_text])
    return data


if __name__ == '__main__':

    dataset = sys.argv[1]
    train_path = os.path.join('../data/', dataset, 'train_new.tsv')
    dev_path = os.path.join('../data', dataset, 'dev_new.tsv')
    test_path = os.path.join('../data/', dataset, 'test_new.tsv')
    pca_path = os.path.join('../data/', dataset, 'pca.csv')
    label_path = os.path.join('../data/', dataset, 'sent_labels.csv')
    text_path = os.path.join('../data/', dataset, 'text.csv')

    train_file = csv.reader(open(train_path), delimiter='\t', quotechar='"')
    dev_file = csv.reader(open(dev_path), delimiter='\t', quotechar='"')
    test_file = csv.reader(open(test_path), delimiter='\t', quotechar='"')
    pca_file = csv.reader(open(pca_path), delimiter=',', quotechar='"')
    label_file = csv.reader(open(label_path), delimiter=',', quotechar='"')
    text_file = csv.reader(open(text_path), delimiter=',', quotechar='"')

    #Reading in all required data and metadata
    #Text is read in from input file to CSM, because output filters stopwords
    train_metadata = read_ids_and_labels(train_file)
    dev_metadata = read_ids_and_labels(dev_file)
    test_metadata = read_ids_and_labels(test_file)

    text_data = read_text(text_file)
    topic_data = read_topic_labels(text_data, label_file)

    #Reading PCA output and constructing schema-weights variable according to pre-decided schemas
    #This step can be edited to automatically identify schemas based on loading cutoff
    schemas = [[2,4,8], [1,4], [1,2,4,6,8], [1,3,5,9], [5,7,8,9]] if dataset == 'movies' else [[3,4,5,7], [5,6,7,9], [3,4,5], [3,4,7,9], [2,3,4,6]]
    schema_weights = read_pca_file(schemas, pca_file)

    #For each document, for each schema compute a score. Highest-scoring schema is assigned to document
    #Doing it for train, dev and test data separately
    train_data = assign_schemas(train_metadata, topic_data, schema_weights)
    dev_data = assign_schemas(dev_metadata, topic_data, schema_weights)
    test_data = assign_schemas(test_metadata, topic_data, schema_weights)
    
    schema_counts = [0.0]*5
    for sample in train_data:
        schema_counts[sample[2]] += 1
    print(schema_counts)

    #Storing train, dev and test data in jsonl format to preserve (sentence, topic) structure
    train_out = open(os.path.join('../data/', dataset, 'train_with_schema.jsonl'), 'w')
    dev_out = open(os.path.join('../data/', dataset, 'dev_with_schema.jsonl'), 'w')
    test_out = open(os.path.join('../data/', dataset, 'test_with_schema.jsonl'), 'w')
    for sample in train_data:
        train_out.write(json.dumps(sample)+'\n')
    for sample in dev_data:
        dev_out.write(json.dumps(sample)+'\n')
    for sample in test_data:
        test_out.write(json.dumps(sample)+'\n')
    train_out.close()
    dev_out.close()
    test_out.close()
