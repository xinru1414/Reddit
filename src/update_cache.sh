echo `date` >> /logs/crawl_log.txt
echo ============================= >> /logs/crawl_log.txt
#python3.7 src/crawl_reddit.py -S resources/subreddit_groups/forums_environmental.txt >> /logs/crawl_log.txt
#python3.7 src/crawl_reddit.py -S resources/subreddit_groups/forums_abortion.txt >> /logs/crawl_log.txt
#python3.7 src/crawl_reddit.py -S resources/subreddit_groups/forums_lgbt.txt >> /logs/crawl_log.txt
#python3.7 src/crawl_reddit.py -S resources/subreddit_groups/forums_lisa.txt >> /logs/crawl_log.txt
#python3.7 src/crawl_reddit.py -S resources/subreddit_groups/forums_rust.txt >> /logs/crawl_log.txt

pipenv run python src/crawl_reddit.py -d reddit-environmental -S resources/subreddit_groups/forums_enviromental.txt >> /logs/crawl_log.txt
pipenv run python src/crawl_reddit.py -d reddit-abortion -S resources/subreddit_groups/forums_abortion.txt >> /logs/crawl_log.txt
pipenv run python src/crawl_reddit.py -d reddit-lgbt -S resources/subreddit_groups/forums_lgbt.txt >> /logs/crawl_log.txt
pipenv run python src/crawl_reddit.py -d reddit-lisa -S resources/subreddit_groups/forums_lisa.txt >> /logs/crawl_log.txt
pipenv run python src/crawl_reddit.py -d reddit-rust -S resources/subreddit_groups/forums_rust.txt >> /logs/crawl_log.txt
