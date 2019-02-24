import mysql.connector
import os

db = "discoursedb_ext_EnviroReddit"
posts = "/usr2/Reddit/data/posts/"

connection = mysql.connector.connect(
            host= "localhost",
            user= "local",
            password= "local",
            database= db
        );
cur = connection.cursor(dictionary=True);

cur.execute("""select entity_source_id from data_source_instance where entity_source_descriptor = 'reddit#id#POST';""")
keys = {row["entity_source_id"] for row in cur.fetchall()}

keys2 = {fn.split(".")[0]  for fn in os.listdir(posts)}

print "Found ", len(keys), "keys in",db," versus",len(keys2),"keys in directory"

print "\n".join(list(keys2.difference(keys))[:1000])
