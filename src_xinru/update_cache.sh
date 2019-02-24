#!/bin/bash
cd /usr2/Reddit
. src/env/bin/activate
python3.7 src/crawl_reddit.py -S forums.txt
python3.7 src/crawl_reddit.py -S forums_lgbt.txt
python3.7 src/crawl_reddit.py -A data/top_users_20181219_unique.txt
#python3.7 src/crawl_reddit.py -A data/top_users_lgbt_20190130_unique.txt
