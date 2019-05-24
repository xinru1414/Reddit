#!/bin/bash
POSTSFILE=tmp/posts`date +%Y%m%d_%H%M`.csv
echo "---------STARTING----------" `date` >> ddb_log.txt
python3.7 src/gen_discoursedb_csv.py -o $POSTSFILE -d EnviroReddit -S resources/subreddit_groups/forums_environmental.txt &>> logs/ddb_log.txt
echo "--------IMPORTING----------" `date` >> ddb_log.txt
bash /usr2/scratch/discoursedb_v09/discoursedb-core/discoursedb-io-csv/import_posts $POSTSFILE discoursedb_ext_EnviroReddit &>> logs/ddb_log.txt
echo "--------DONE----------" `date` >> ddb_log.txt
