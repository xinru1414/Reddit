"""
May 2019
Xinru Yan

This is a script for grabbing all post_ids in a mongodb collection and put them in a file as an input to pull_reddit_comment.py
Usage:
    python grab_post_id.py -d MONGODB_NAME -o OUTPUTFILE
    (e.g. -d reddit-environmental -o resources/post_ids_for_comments/reddit-environmental.txt)
"""

import click
from pymongo import MongoClient


@click.command()
@click.option('-d', '--database', 'database', type=str)
@click.option('-o', '--output', 'output', type=str)
def main(database, output):
    myclient = MongoClient("mongodb://127.0.0.1:27017")
    mydb = myclient[database]
    mycol = mydb["posts"]
    with open(output, 'w') as fp:
        for x in mycol.find({},{"id": 1,"_id": 0}):
            for id in x:
                fp.write(x[id] + '\n')


if __name__ == '__main__':
    main()