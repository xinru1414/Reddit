#!/bin/bash
cd /usr2/scratch/cbogart/Reddit
. src/env/bin/activate
echo "---------STARTING----------" `date` >> ddb_log.txt
python3.7 src/gen_discoursedb_csv.py -S forums.txt -A data/top_users_20181219_unique.txt &>> ddb_log.txt
echo "--------IMPORTING----------" `date` >> ddb_log.txt
bash /usr2/scratch/discoursedb_v09/discoursedb-core/discoursedb-io-csv/import_posts posts.csv discoursedb_ext_EnviroReddit &>> ddb_log.txt
echo "--------DONE----------" `date` >> ddb_log.txt
