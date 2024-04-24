import asyncio, traceback, random
from config import create_api
import time, json, os, psycopg2
from pprint import pformat, pprint
from datetime import datetime
import pandas as pd
import tweepy
import logging


def get_current_path(dirr=""):
    patth = os.path.abspath(os.path.dirname(__file__))
    if dirr != "":
        patth += f"/{dirr}"
    if not os.path.exists(patth):
        os.mkdir(patth)
    return patth


logging.basicConfig(
    filename=f"{get_current_path('twbots_out')}/LOGS_tweet_fan.out",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%D %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger()


async def main():
    api, cl = create_api()
    #followers_ids = api.get_follower_ids()
    #print(f"{len(followers_ids)=}")
    with open("./friends_to_unfollow.json","r") as ff:
        friends_not_following = json.loads(ff.read())
    with open("./followers_ids.json","r") as f:
        followers = json.loads(f.read())
    #frens = tweepy.Cursor(
    #    api.get_friends,
    #).items(5000)
    frens = api.get_friends(cursor=-1,count=10)
    #pprint(frens)
    count = 0
    #pprint(frens)
    pprint(type(frens))
    for fr in frens:
        try:
            print("\n\n\n")
            print(fr)
            print(len(fr))
            continue
            fr = fr[0]
            print(fr)
            print(f"{count=} / {fr._json['name']}")
            count+=1
            if int(fr._json['id']) not in followers:
                print(f"    Not following")
                if int(fr._json['id']) not in friends_not_following:
                    friends_not_following.append(int(fr._json['id']))
                    with open(f"./friends_to_unfollow.json","w") as ff:
                        ff.write(json.dumps(friends_not_following,indent=4))   
                        print(f"{len(friends_not_following)=}")
        except:
            print("Exception")
            traceback.print_exc()
            break
        finally:
            print(f"{len(friends_not_following)=}")

if __name__ == "__main__":
    asyncio.run(main())

