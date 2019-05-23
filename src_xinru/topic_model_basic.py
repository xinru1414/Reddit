import re
import sys,os
import gensim
from gensim import corpora

# https://www.analyticsvidhya.com/blog/2016/08/beginners-guide-to-topic-modeling-in-python/

def main():

    event_dir = sys.argv[1]

    all_events = []
    for filename in os.listdir(event_dir):
        text = open(os.path.join(event_dir,filename)).read()
        events = re.findall(r'<event.*?>(.*?)</event>', text)
        print(events)
        all_events.append(events)
    print(len(all_events))

    dictionary = corpora.Dictionary(all_events)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in all_events]

    Lda = gensim.models.ldamodel.LdaModel

    ldamodel = Lda(doc_term_matrix, num_topics=30, id2word=dictionary, passes=50)
    print(ldamodel.print_topics(num_topics=30, num_words=10))

if __name__ == '__main__':
    main()