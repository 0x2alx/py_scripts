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

PGC = None

RUN_ID = None

MY_USR_ID = 1482489320430837764

# LIKE, RT, FOLLOW
COUNTERS = [0, 0, 0]

FRIENDS_LIST = []
RATE_RTED_POST = {
    "tstamps": [],
    "rate": 50,
    "period": 900,
    "sleep": True,
    "desc": "RETWEETS",
}
RATE_LIKED_POST = {
    "tstamps": [],
    "rate": 50,
    "period": 900,
    "sleep": True,
    "desc": "LIKES",
}
RATE_FOLLOWED_POST = {
    "tstamps": [],
    "rate": 50,
    "period": 900,
    "rate2": 400,
    "period2": 86400,
    "sleep": True,
    "desc": "FOLLOW",
}
RATE_LIMIT_REQ = {
    "tstamps": [],
    "rate": 180,
    "period": 900,
    "sleep": True,
    "desc": "RATE",
}

RATE_LIMIT_QUERRY_THRESHOLD = 0.5

MY_FRIENDS_IDS = []

DEF_SINCE_ID = 1524294196202553344
SEP = "###################################################################################"
SEP2 = "#################################"


async def check_post_limits():
    logger.info(f"\t CHECKING POST LIMITS")
    should_wait = 0
    busted_rates = []
    global RATE_RTED_POST
    global RATE_LIKED_POST
    global RATE_FOLLOWED_POST
    global RATE_LIMIT_REQ

    noww = int(time.time())

    ALL_RATES = [
        RATE_RTED_POST,
        RATE_LIKED_POST,
        RATE_FOLLOWED_POST,
        RATE_LIMIT_REQ,
    ]

    treshold_rate = 0.75
    sleep_multiplier = 0.8
    for rate in ALL_RATES:
        oldest_tweet = 99999999999999999999999999
        lowest_tstamp = int(noww - rate["period"])
        logger.info(f"\t rate['period']: {rate['period']}")
        temp_array = []
        for ind, ts in enumerate(rate["tstamps"]):
            # logger.info(
            #    f"\t int(ts): {int(ts)} > lowest_tstamp: {lowest_tstamp} {int(ts) > lowest_tstamp}"
            # )
            if int(ts) > lowest_tstamp:
                temp_array.append(int(ts))
            if int(ts) < oldest_tweet:
                oldest_tweet = int(ts)
        nb_posts = len(temp_array)

        logger.info(
            f"\t RATE LIMIT FOR {rate['desc']}: {nb_posts}/{int(rate['rate'])} --- {nb_posts / int(rate['rate'])} "
            + f"--- {(nb_posts / int(rate['rate'])) >= treshold_rate} --- PREV: {len(rate['tstamps'])}/{int(rate['rate'])} --- {len(rate['tstamps']) / int(rate['rate'])}"
        )
        if rate["desc"] == "RETWEETS":
            RATE_RTED_POST["tstamps"] = temp_array
        if rate["desc"] == "LIKES":
            RATE_LIKED_POST["tstamps"] = temp_array
        if rate["desc"] == "FOLLOW":
            RATE_FOLLOWED_POST["tstamps"] = temp_array
        if rate["desc"] == "RATE":
            RATE_LIMIT_REQ["tstamps"] = temp_array

        if nb_posts / int(rate["rate"]) >= treshold_rate:
            logger.info(
                f"\t RATE LIMIT FOR {rate['desc']} DANGEROUS. NEEDS SLEEP nb_posts: {nb_posts}/{int(rate['rate'])} --- {nb_posts / int(rate['rate'])} --- {(nb_posts / int(rate['rate'])) >= treshold_rate}"
            )
            waiting_time = noww - oldest_tweet
            if waiting_time > int(rate["period"]):
                should_wait = int(rate["period"]) * sleep_multiplier
            elif waiting_time > should_wait:
                should_wait = waiting_time * sleep_multiplier
            busted_rates.append(rate["desc"])
    await update_rates_in_db()
    return should_wait, busted_rates


async def load_rates_from_db():
    global RATE_RTED_POST
    global RATE_LIKED_POST
    global RATE_FOLLOWED_POST
    global RATE_LIMIT_REQ
    conn = connect_pg()
    exe_str = "SELECT * FROM tweet_sales_bot.tweet_rate_counters order by id asc"
    dat = pd.read_sql_query(exe_str, conn)
    conn.close()
    if dat.empty:
        logger.info(f"\t Empty table...")
        return
    RATE_RTED_POST = dat["json_dict"].iloc[0]
    RATE_LIKED_POST = dat["json_dict"].iloc[1]
    RATE_FOLLOWED_POST = dat["json_dict"].iloc[2]
    RATE_LIMIT_REQ = dat["json_dict"].iloc[3]


async def update_rates_in_db():
    conn = connect_pg()
    curr = conn.cursor()
    curr.execute(
        "UPDATE rate_counters SET json_dict=%s where id=1",
        (json.dumps(RATE_RTED_POST),),
    )
    curr.execute(
        "UPDATE rate_counters SET json_dict=%s where id=2",
        (json.dumps(RATE_LIKED_POST),),
    )
    curr.execute(
        "UPDATE rate_counters SET json_dict=%s where id=3",
        (json.dumps(RATE_FOLLOWED_POST),),
    )
    curr.execute(
        "UPDATE rate_counters SET json_dict=%s where id=4",
        (json.dumps(RATE_LIMIT_REQ),),
    )
    conn.commit()
    curr.close()
    conn.close()


async def fetch_friend_list_from_db():
    global FRIENDS_LIST
    conn = connect_pg()
    exe_str = "SELECT * FROM tweet_sales_bot.tweet_friends_list order by id asc"
    dat = pd.read_sql_query(exe_str, conn)
    conn.close()
    if dat.empty:
        logger.info(f"\t Empty table...")
        return
    for index, row in dat.iterrows():
        logger.info(
            f"\t index: {index} -- row_id: {row['id']} -- row_json: {row['json_data']}"
        )
        FRIENDS_LIST.append(row["json_data"])


async def updates_friend_list_in_db():
    conn = connect_pg()
    curr = conn.cursor()
    c = 1
    for fr in FRIENDS_LIST:
        # logger.info(f"\t fr: {fr} -- id: {c}")
        curr.execute(
            "UPDATE tweet_sales_bot.tweet_friends_list SET json_data=%s where id=%s",
            (
                json.dumps(fr),
                c,
            ),
        )
        c += 1
    conn.commit()
    curr.close()
    conn.close()


async def get_user_timeline(api, cl, ind):
    global FRIENDS_LIST
    global MY_FRIENDS_IDS
    global COUNTERS
    user = FRIENDS_LIST[ind]["usr"]
    since_id = DEF_SINCE_ID
    if FRIENDS_LIST[ind]["last_rted"] > 0:
        since_id = FRIENDS_LIST[ind]["last_rted"]
    if since_id < 1531624400214278147:
        since_id = 1531624400214278147

    tweets = tweepy.Cursor(
        api.user_timeline,
        screen_name=user,
        include_rts=True,
        since_id=since_id,
    ).items(50)
    logger.info(" " + "\n" + SEP + "\n" + user + "\n" + SEP)
    loop_ind = 0
    for tweet in tweets:
        logger.info(SEP2)
        loop_sleep = 0
        if loop_ind % 10 == 0 and loop_ind != 0:
            logger.info(f"\t CHECKING RATE LIMIT iteration: {loop_ind}")
            logger.info(SEP2)
            sleep_val, busted_rates = await check_post_limits()
            logger.info(f"\t CHECKING RATE LIMIT {sleep_val} --- {busted_rates}")
            if len(busted_rates) == 0:
                if loop_ind % 60 == 0:
                    await check_rate_limit(api, cl)
            if len(busted_rates) > 1 or (
                len(busted_rates) == 1 and busted_rates[0] != "RATE"
            ):
                logger.info(f"\t POST RATE LIMIT SLEEP for {user}: {sleep_val} \n\n\n")
                await asyncio.sleep(sleep_val)
                api, cl = create_api()
        tw_id = tweet._json["id"]
        logger.info(f"\t tweet: {tw_id}")
        check_mentions = False

        if not FRIENDS_LIST[ind]["full_supp"] and random.choice([True, False]):
            logger.info(f"\t\t ------------ RAND Skipping tweet {tw_id}")
            continue
        try:
            # Not RTed yet
            if not tweet._json["retweeted"]:
                logger.info(f"\t NOT RTed yet")
                # Not a Comment
                if (
                    "in_reply_to_status_id" not in tweet._json
                    or tweet._json["in_reply_to_status_id"] == None
                ):
                    logger.info(f"\t RETWEETING: {tw_id}")
                    loop_sleep = 3 * random.random() + random.random()
                    cl.retweet(tw_id)
                    COUNTERS[0] += 1
                    check_mentions = True
                    RATE_RTED_POST["tstamps"].append(int(time.time()))
                    logger.info(
                        f"\t appending to RATE_RTED_POST: {int(time.time())} - len: {len(RATE_RTED_POST['tstamps'])}"
                    )
                    sleep_val = 5 * random.random() + random.random()
                    logger.info(f"\t sleep_val: {sleep_val}")
                    await asyncio.sleep(sleep_val)
                    logger.info(f"\t RETWEEEETEDDDDD: {tw_id}")
                try:
                    logger.info(
                        f"\t Is RT {'retweeted_status' in tweet._json} -- Is Comment: {'in_reply_to_status_id' in tweet._json} - {tweet._json['in_reply_to_status_id'] != None}"
                    )
                except:
                    logger.error(f"\t Error logging RT shit")
            # NOT Liked yet
            if not tweet._json["favorited"]:
                logger.info(f"\t LIKING: {tw_id}")
                loop_sleep = 3 * random.random() + random.random()
                cl.like(tw_id)
                COUNTERS[1] += 1
                check_mentions = True
                RATE_LIKED_POST["tstamps"].append(int(time.time()))
                logger.info(
                    f"\t appending to RATE_LIKED_POST: {int(time.time())} - len: {len(RATE_LIKED_POST['tstamps'])}"
                )
                sleep_val = 5 * random.random() + random.random()
                logger.info(f"\t sleep_val: {sleep_val}")
                await asyncio.sleep(sleep_val)
                logger.info(f"\t LIKEDDDD: {tw_id}")
            loop_ind += 1
            if int(tw_id) > int(since_id):
                FRIENDS_LIST[ind]["last_rted"] = tw_id
            # FOLLOW MENTIONS
            if (
                "entities" in tweet._json
                and check_mentions
                and FRIENDS_LIST[ind]["full_supp"]
                and user == "ghooost0x2a"
            ):
                if "user_mentions" in tweet._json["entities"]:
                    for usr in tweet._json["entities"]["user_mentions"]:
                        logger.info(f"\t MENTIONS: {usr}")
                        if (
                            int(usr["id"]) not in MY_FRIENDS_IDS
                            and int(usr["id"]) != MY_USR_ID
                        ):
                            logger.info(f"\t NOT FOLLOWING YET!!!!")
                            cl.follow_user(usr["id"])
                            COUNTERS[2] += 1
                            RATE_FOLLOWED_POST["tstamps"].append(int(time.time()))
                            logger.info(
                                f"\t appending to RATE_FOLLOWED_POST: {int(time.time())} - len: {len(RATE_FOLLOWED_POST['tstamps'])}"
                            )
                            logger.info(f"\t JUST FOLLOWED: {usr['screen_name']}")
                            MY_FRIENDS_IDS.append(int(usr["id"]))
                            logger.info(
                                f"\t UPDATED MY_FRIENDS_IDS[-1]: {MY_FRIENDS_IDS[-1]} -- len {len(MY_FRIENDS_IDS)}"
                            )
                            sleep_val = 3 * random.random() + random.random()
                            logger.info(f"\t sleep_val: {sleep_val}")
                            await asyncio.sleep(sleep_val)
        except:
            logger.error(f"\t ERROR with TWEET: {tw_id}")
            traceback.print_exc()
        if loop_sleep > 0:
            logger.info(f"\t SLEEEPINGGGGGG FOR: {loop_sleep}")
            await asyncio.sleep(loop_sleep)
        # return
    logger.info(f"\t TOTAL NB TWEETS: {loop_ind+1} for {user}")


async def check_rate_limit(api, cl):
    sleep_needed_for = 0
    try:
        rate_status = api.rate_limit_status()
        RATE_LIMIT_REQ["tstamps"].append(int(time.time()))
        logger.info(
            f"\t appending to RATE_LIMIT_REQ: {int(time.time())} - len: {len(RATE_LIMIT_REQ['tstamps'])}"
        )
        pprint(type(rate_status["resources"]))
        for cat, val in rate_status["resources"].items():
            for key, lim in val.items():
                limit_int = int(lim["limit"])
                remaining_int = int(lim["remaining"])
                reset_int = int(lim["reset"])
                if limit_int != remaining_int:
                    logger.info(f"\t lim: {lim} ---- {key}")
                    if remaining_int / limit_int <= 0.2:
                        logger.info(f"\t RATE LIMIT IS LOW: {remaining_int/limit_int}")
                        if int(reset_int - int(time.time())) > sleep_needed_for:
                            sleep_needed_for = int(reset_int - int(time.time()))
    except:
        logger.error(f"\t ERROR with RATE LIMIT CHECKER")
        traceback.print_exc()
    if sleep_needed_for > 0:
        logger.info(f"\t RATE LIMITING, ABOUT TO SLEEP FOR: {sleep_needed_for/2}")
        await asyncio.sleep(sleep_needed_for / 2)
    else:
        logger.info("\t RATE LIMIT OK")


async def update_run_status(id=-1):
    global RUN_ID
    conn = connect_pg()
    curr = conn.cursor()
    exe_string = ""
    tstamp = datetime.today().strftime("%Y-%m-%d %I:%M:%S-4")
    vars = ()
    if id == -1:
        exe_string = "INSERT INTO tweet_sales_bot.tweet_sales_bot_runs (start_time) VALUES (%s) RETURNING id"
        vars = (tstamp,)
    else:
        exe_string = "UPDATE tweet_sales_bot.tweet_sales_bot_runs SET end_time=%s, smooth_run=TRUE WHERE id=%s RETURNING id"
        vars = (
            tstamp,
            id,
        )
    logger.info(f"\t exe_string: {exe_string} -- vars: {vars}")
    curr.execute(exe_string, vars)
    RUN_ID = curr.fetchone()[0]
    conn.commit()
    curr.close()
    logger.info(f"\t RUN_ID: {RUN_ID}")


async def check_last_run_finished():
    conn = connect_pg()
    exe_str = (
        "SELECT * FROM tweet_sales_bot.tweet_sales_bot_runs order by id desc limit 1"
    )
    dat = pd.read_sql_query(exe_str, conn)
    conn.close()
    if dat.empty:
        logger.info(f"\t Empty table...")
        return
    smooth_run = dat["smooth_run"].iloc[0]
    end_time = dat["end_time"].iloc[0]
    start_time = dat["start_time"].iloc[0]
    if not smooth_run and end_time == None and False:
        logger.warning(f"\t Last execution still running...started at: {start_time}")
        logger.warning(f"\t Exiting...")
        exit(0)


def connect_pg():
    logger.info(f"\t connecting to postgres")
    try:
        return psycopg2.connect(
            "host='{}' port={} dbname='{}' user={} password={}".format(
                "192.168.0.142", 4201, "tweet_bot", "tweet_bot_user", ".POSTltw1"
            )
        )
    except:
        logger.error(f"\t ERROR connecting to Postgres...")
        traceback.print_exc()
        exit(1)


def print_rates_objs():
    ALL_RATES = [
        RATE_RTED_POST,
        RATE_LIKED_POST,
        RATE_FOLLOWED_POST,
        RATE_LIMIT_REQ,
    ]

    for v in ALL_RATES:
        logger.info(f"\t ALL_RATES: {v}")


async def main():

    api, cl = create_api()
    print(api.get_followers(count=10))
    return 0
    logger.info("\t ############### TWEET BOT MAIN() ###############")
    await fetch_friend_list_from_db()
    await check_last_run_finished()
    await load_rates_from_db()
    # print_rates_objs()
    sleep_val, busted_rates = await check_post_limits()
    if len(busted_rates) == 0:
        await check_rate_limit(api, cl)
    if len(busted_rates) > 1 or (len(busted_rates) == 1 and busted_rates[0] != "RATE"):
        logger.info(f"\t POST RATE SLEEP: {sleep_val} --- {busted_rates} \n\n\n")
        await asyncio.sleep(sleep_val)
    print_rates_objs()
    # return
    await update_run_status()
    logger.info("\t TWITTER api: " + str(api))
    global MY_FRIENDS_IDS
    global COUNTERS
    MY_FRIENDS_IDS = api.get_friend_ids(user_id="ghost_42a")
    logger.info(f"\t MY_FRIENDS len: {len(MY_FRIENDS_IDS)}")
    await asyncio.sleep(1)
    await check_rate_limit(api, cl)
    while True:
        api, cl = create_api()
        COUNTERS = [0, 0, 0]
        for fren in range(0, len(FRIENDS_LIST)):
            await get_user_timeline(api, cl, fren)
            logger.info(f"\t FOR LOOP SLEEEPP.......")
            await asyncio.sleep(3 * random.random() + random.random())
            sleep_val, busted_rates = await check_post_limits()
            if len(busted_rates) == 0:
                await check_rate_limit(api, cl)
            if len(busted_rates) > 1 or (
                len(busted_rates) == 1 and busted_rates[0] != "RATE"
            ):
                logger.info(
                    f"\t POST RATE SLEEP for {fren}: {sleep_val} --- {busted_rates} \n\n\n"
                )
                await asyncio.sleep(sleep_val)
            # break
            await updates_friend_list_in_db()
        logger.info(
            f"\t LAST RUN: LIIKES = {COUNTERS[1]} -- RTs = {COUNTERS[0]} -- FOLLOWS = {COUNTERS[2]}"
        )
        await update_run_status(RUN_ID)
        return


if __name__ == "__main__":
    asyncio.run(main())

"""
FRIENDS_LIST = [
    {"usr": "ghooost0x2a", "last_rted": 1529110274468454401, "full_supp": True},
    {"usr": "meowgress", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "avril15sales", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "CrazySassyExes", "last_rted": 1529110274468454401, "full_supp": True},
    {"usr": "Leopardslunch_", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "avril15NFT", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "demondeathcult", "last_rted": 1529110274468454401, "full_supp": True},
    {"usr": "psychedemon", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "madison_nft", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "Cho_Though", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "KasparK_nft", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "youareinmymovie", "last_rted": 1529110274468454401, "full_supp": True},
    {"usr": "StudioIrida", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "Jen_Donohue", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "naehrstff_nft", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "gaurand_eth", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "RealKatoOG", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "iamcranksy", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "MacBher", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "cosmikflo", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "badluckspence", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "BenjaminBitcoin", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "jonna2211", "last_rted": 1529110274468454401, "full_supp": False},
    {"usr": "niftyJB", "last_rted": 1529110274468454401, "full_supp": False},
]
def write_tweets_to_file(tweet_js):
    f = open("temp_tweets.json", "a")
    f.write(json.dumps(tweet_js, indent=3))
    f.close()

def test_post_limist():
    logger.info(f"\t FILLING POST LIMITS")
    global RATE_RTED_POST
    global RATE_LIKED_POST
    global RATE_FOLLOWED_POST
    global RATE_LIMIT_REQ

    noww = time.time()
    older_than_900 = int(noww - 1200)
    newer_than_900 = int(noww - 500)

    default_tstamps1 = []
    default_tstamps2 = []
    default_tstamps3 = []
    default_tstamps4 = []

    for i in range(0, 10):
        default_tstamps1.append(older_than_900)
        default_tstamps2.append(older_than_900)
        default_tstamps3.append(older_than_900)
        default_tstamps4.append(older_than_900)
    for i in range(0, 10):
        default_tstamps1.append(newer_than_900)
        default_tstamps2.append(newer_than_900)
        default_tstamps3.append(newer_than_900)
        default_tstamps4.append(newer_than_900)
    for i in range(0, 10):
        default_tstamps1.append(older_than_900)
        default_tstamps2.append(older_than_900)
        default_tstamps3.append(older_than_900)
        default_tstamps4.append(older_than_900)
    for i in range(0, 10):
        default_tstamps1.append(newer_than_900)
        default_tstamps2.append(newer_than_900)
        default_tstamps3.append(newer_than_900)
        default_tstamps4.append(newer_than_900)

    ALL_RATES = [
        RATE_RTED_POST,
        RATE_LIKED_POST,
        RATE_FOLLOWED_POST,
        RATE_LIMIT_REQ,
    ]

    RATE_RTED_POST["tstamps"] = default_tstamps1
    RATE_LIKED_POST["tstamps"] = default_tstamps2
    RATE_FOLLOWED_POST["tstamps"] = default_tstamps3
    RATE_LIMIT_REQ["tstamps"] = default_tstamps4

    for rate in ALL_RATES:
        logger.info(f"\t POST RATE {rate}")
        logger.info(f"\t rate['tstamps'] ---- {rate['tstamps']}")


def write_rates_to_file():
    global RATE_RTED_POST
    global RATE_LIKED_POST
    global RATE_FOLLOWED_POST
    global RATE_LIMIT_REQ
    ALL_RATES = [
        RATE_RTED_POST,
        RATE_LIKED_POST,
        RATE_FOLLOWED_POST,
        RATE_LIMIT_REQ,
    ]
    logger.info(f"\t writing ALL_RATES: {pformat(ALL_RATES)}")
    try:
        f = open(RATES_FILE, "w")
        f.write(json.dumps(ALL_RATES, indent=3))
        f.close()
    except:
        logger.error(f"\t Error writing rates file {RATES_FILE}")
        traceback.print_exc()

def post_rates_above_threshold():
    ALL_RATES = [
        RATE_RTED_POST,
        RATE_LIKED_POST,
        RATE_FOLLOWED_POST,
        RATE_LIMIT_REQ,
    ]
    for rate in ALL_RATES:
        logger.info(
            f"\t post_rates_above_threshold(): {len(rate['tstamps'])}/{int(rate['rate'])} = {len(rate['tstamps'])/int(rate['rate'])}"
        )
        if len(rate["tstamps"]) / int(rate["rate"]) >= RATE_LIMIT_QUERRY_THRESHOLD:
            return True

    return False


def load_rates_from_file():
    global RATE_RTED_POST
    global RATE_LIKED_POST
    global RATE_FOLLOWED_POST
    global RATE_LIMIT_REQ
    # logger.info(f"\t ALL_RATES pre-load: {pformat(ALL_RATES)}")
    if os.path.exists(RATES_FILE):
        try:
            f = open(RATES_FILE, "r")
            ratess = json.loads(f.read())
            f.close()
            if len(ratess) > 0:
                RATE_RTED_POST = ratess[0]
                RATE_LIKED_POST = ratess[1]
                RATE_FOLLOWED_POST = ratess[2]
                RATE_LIMIT_REQ = ratess[3]
        except:
            logger.error(f"\t Error loading rates file {RATES_FILE}")
            traceback.print_exc()
    else:
        logger.info(f"\t {RATES_FILE} doesn't exist...")
        return
    logger.info(f"\t ALL_RATES loaded from file....")

"""
