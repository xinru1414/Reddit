"""
Event exploring
Usage:
    python event_explore.py ../events
"""
import re
import sys,os
import string
from collections import Counter
import nltk

def events(dir):
    all_events = []
    for filename in os.listdir(dir):
        text = open(os.path.join(dir,filename)).read()
        events = re.findall(r'<event.*?>(.*?)</event>', text)
        print('File '+ os.path.join(dir,filename) + ' :' + str(Counter(events).most_common()))
        all_events = all_events + events
    print(Counter(all_events).most_common(20))

def strip_punctuation(s):
    return ''.join(c for c in s if c not in string.punctuation)

def stats(dir):
    stopwords = nltk.corpus.stopwords.words('english')
    all_text = ''
    for filename in os.listdir(dir):
        text = open(os.path.join(dir,filename)).read()
        text = strip_punctuation(text)
        all_text += text
        allWords = nltk.tokenize.word_tokenize(text)
        allWordDist = nltk.FreqDist(w.lower() for w in allWords if w.lower() not in stopwords)
        print('File '+ os.path.join(dir,filename) + ' :' + str(allWordDist.most_common(20)))
    all_words = nltk.tokenize.word_tokenize(all_text)
    all_word_Dist = nltk.FreqDist(w.lower() for w in all_words if w.lower() not in stopwords)
    print('Final ' + str(all_word_Dist.most_common(50)))

def main():

    # event_dir = sys.argv[1]
    # events(event_dir)
    stats_dir = sys.argv[1]
    stats(stats_dir)

if __name__ == '__main__':
    main()