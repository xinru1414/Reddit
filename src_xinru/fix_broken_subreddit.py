import json
import os
import tqdm

oj = { "posts":[], "newest_time": 0}
forum = "environment"

for f in tqdm.tqdm(os.listdir("data/posts")):
    inf = json.load(open("data/posts/" + f,"rb"))
    if "subreddit" in inf and inf["subreddit"].lower() == forum.lower():
        oj["posts"].append(inf["id"])
        if inf["created"] > oj["newest_time"]: oj["newest_time"] = int(inf["created"])
json.dump(oj, open("data/subreddits/" + forum + ".json","w"), indent=4)
