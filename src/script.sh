#!/bin/bash
python crawl_reddit.py -l 1000 -s MakeupAddiction
python top_user_posts.py -s MakeupAddiction -n 20
python explore.py