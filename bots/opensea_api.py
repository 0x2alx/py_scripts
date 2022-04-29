# -*- coding: utf-8 -*-

#####################################################
# OpenSea recent sales pot
# python port from 0xEssential's JS version
# https://github.com/0xEssential/opensea-discord-bot
# OpenSea docs: https://docs.opensea.io/reference/retrieving-asset-events
#####################################################

# imports
from operator import methodcaller
import requests
import datetime
import os
import json
import logging
from pprint import pprint
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

DEF_OUT_FILE = "./tweet_bot_out.txt"
# globals
OS_API_KEY = os.getenv("OS_API_KEY")
COLLECTION_SLUG = os.getenv("COLLECTION_SLUG")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# classes

# functions
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_opensea_recent_events():
    seconds = 3600
    hour_ago = (
        int(datetime.datetime.now().timestamp()) - seconds
    )  # in the last hour, run hourly?

    urll = (
        "https://api.opensea.io/api/v1/events?"
        f"&asset_contract_address={CONTRACT_ADDRESS}"
        f"&event_type=successful"
        "&only_opensea=true"
        f"&occurred_after={hour_ago}"
        f"&collection_slug={COLLECTION_SLUG}"
    )
    logger.info(f"OS request URL: {urll}")
    response = requests_retry_session().get(urll, headers={"X-API-KEY": OS_API_KEY})
    logger.info("RESPONSE JSON LENGHT: " + str(len(response.json())))
    # write_out(response.json(), is_json=True)
    return response.json()


def construct_message(item):
    message_params = {
        "buyer_name": item.get("winner_account").get("user").get("username", "Unknown"),
        "seller_name": item.get("seller").get("user").get("username", "Unknown"),
        "asset_name": item.get("asset").get("name"),
        "symbol": item.get("payment_token").get("symbol"),
        "eth_price": float(item.get("total_price")) / 10 ** 18,
        "usd_price": float(item.get("payment_token").get("usd_price"))
        * (float(item.get("total_price")) / 10 ** 18),
        "img_url": item.get("asset").get("image_original_url"),
        "permalink": item.get("asset").get("permalink"),
        "asset_symbol": item.get("asset").get("asset_contract").get("asset_symbol", ""),
        "twitter_username": item.get("asset")
        .get("collection")
        .get("twitter_username", ""),
    }

    # write_out(message_params, is_json=True)

    message = (
        f"{message_params['buyer_name']} has bought {message_params['asset_name']} "
        f"from {message_params['seller_name']} for $ETH {message_params['eth_price']:.2f} "
        f"(USD {message_params['usd_price']:.2f}) \n #{message_params['asset_symbol']}"
        f"#avril15"
        f" \n \n "
        f"{message_params['permalink']}"
    )

    return message


def write_out(msg, is_json=False, out_file=DEF_OUT_FILE, method="a", also_print=False):
    debugg = True
    try:
        if debugg:
            f = open(out_file, method)
        if not is_json:
            if debugg:
                f.write(str(msg))
            if also_print:
                print(str(msg))
        else:
            if debugg:
                f.write(
                    json.dumps(
                        msg,
                        indent=4,
                    )
                )
                f.write("\n\n\n")
            if also_print:
                pprint(msg)
        if debugg:
            f.close()
            print("FILE WRITTEN")
    except:
        print("Bug here!")


if __name__ == "__main__":
    ff = open(DEF_OUT_FILE, "w")
    ff.write("")
    ff.close()
    get_opensea_recent_events()
