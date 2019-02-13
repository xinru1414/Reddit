import mysql.connector
import os
import config

db = "discoursedb_ext_EnviroReddit"
posts = "/usr2/Reddit/data/posts/"

connection = mysql.connector.connect(
            host= config.discoursedb_host,
            user= config.discoursedb_user,
            password= config.discoursedb_password,
            database= db
        );
cur = connection.cursor(dictionary=True);

cur.execute("""select entity_source_id from data_source_instance where entity_source_descriptor = 'reddit#id#POST';""")
keys = {row["entity_source_id"] for row in cur.fetchall()}

keys2 = {fn.split(".")[0]  for fn in os.listdir(posts)}

print "Found ", len(keys), "keys in",db," versus",len(keys2),"keys in directory"

print "\n".join(list(keys2.difference(keys))[:1000])
