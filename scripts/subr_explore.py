'''
Usage
    python subr_explore.py -s SUBREDDIT
'''
from reddit import Reddit
import config
import csv
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import click


exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
# stop words
#stop = set(stopwords.words('english'))

def clean(text):
    # get rid of emojis
    #text = p.clean(text)
    # get rid of links
    text = re.sub(r'\(http\S+\)|http\S+|www.\S+|imgur.\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'•','',text,flags=re.MULTILINE)
    text = re.sub(r'\[|\]', '', text, flags=re.MULTILINE)
    # get rid of puncs
    text = ''.join(w for w in text if w not in exclude)
    text = re.sub(r'\s+', ' ', text, flags=re.MULTILINE)
    return text


@click.command()
@click.option('-S', '--subreddit-list', 'subreddit_list', type=click.File("r"))
def main(subreddit_list):
    reddit = Reddit(config.data_location)
    subreddits = {subredit.strip().split("/")[-1] for subredit in subreddit_list}

    for subreddit in subreddits:
        sub = reddit.get_subreddit(subreddit)
        with open (f'../acl/{subreddit}_user_perline.csv', 'w') as fp:
            csv_file = csv.writer(fp)
            csv_file.writerow(['SeqId', 'InstNo', 'Author', 'Text'])
            for post in sub.posts:
                if 'selftext' in post and post['selftext'] and post['selftext'] != '[removed]' and post['author'] != '[deleted]' and post['author'] != 'AutoModerator':
                    content_post = post.get('selftext').replace('\n', ' ').lower()
                    #clean_text = clean(content_post)
                    #csv_file.writerow([post.get('id'), 0, post['author'], clean_text])
                    content_post = nltk.tokenize.sent_tokenize(content_post)
                    if len(content_post) > 4:
                        count = 0
                        for sent in content_post:
                            sent = clean(sent)
                            sent = nltk.tokenize.word_tokenize(sent)
                            sent = ' '.join(sent)
                            csv_file.writerow([post.get('id'), count, post['subreddit'], sent])
                            count += 1


if __name__ == '__main__':
    main()
