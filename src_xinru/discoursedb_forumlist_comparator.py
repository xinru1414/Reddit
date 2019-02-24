import mysql.connector
import os
import click
from reddit import Reddit
import config

#db = "discoursedb_ext_EnviroReddit"
#posts = "/usr2/Reddit/data/posts/"

connection = mysql.connector.connect(
            host= "localhost",
            user= "local",
            password= "local",
            database= db
        );
cur = connection.cursor(dictionary=True);
reddit = Reddit(config.data_location)

@click.command()
@click.option('-S', '--subreddit-list', 'subreddit_file' type=click.File("r"))
@click.option('-D', '--database', 'database', type=str, default="discoursedb_ext_EnviroReddit")
def main(subreddit_file, database):
    cur.execute("""select entity_source_id from data_source_instance where entity_source_descriptor = 'reddit#id#POST';""")
    keys = {row["entity_source_id"] for row in cur.fetchall()}
    
    subreddits = {s.strip() for s in subreddit_file}
    keys2 = set()
    for subreddit in subreddits:
        s = Reddit.get_subreddit(subreddit)
        keys2.extend({p["id"] for p in s.posts})
    
    print "Found ", len(keys), "keys in",db," versus",len(keys2),"keys in directory"
    
    print "\n".join(list(keys2.difference(keys))[:1000])
