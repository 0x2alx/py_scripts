# -*- coding: utf-8 -*-
# https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials

# import tweepy
import logging
from config import create_api
from opensea_api import get_opensea_recent_events, construct_message, write_out
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def check_recent_sales(api, event_id):
    logger.info("Calling OpenSea")
    dct = get_opensea_recent_events().get("asset_events")
    logger.info("OS request returned " + str(len(dct)) + " events")
    if len(dct) == 0:
        return event_id

    new_event_id = 69
    try:
        new_event_id = int(dct[0].get("id"))
    except:
        logger.info("No EVENTS returned")
        logger.info(dct)
    logger.info(f"current event_id {event_id} \n  most recent event_id {new_event_id}")

    # first run, we simply record the last sale
    if event_id == 42 and new_event_id != 69:
        permalink = dct[0].get("asset").get("permalink")
        logger.info(f"PERMALINK: {permalink}")
        return new_event_id
    # if it's first run, but there are no sales returned in the defined period
    elif new_event_id == 69 and event_id == 42:
        return event_id

    permalink = dct.get("asset").get("permalink")
    logger.info(f"PERMALINK: {permalink}")
    for k, v in enumerate(dct):
        ev_id = v["id"]
        if int(v["id"]) <= event_id:
            break
        logger.info(f"New event: {ev_id}")
        msg = construct_message(v)
        logger.info(f"Constructed TWEET: {msg}")
        time.sleep(1)  # not to annoy twitter API too much
        api.update_status(status=msg)

    return new_event_id


def main():
    api = create_api()
    event_id = 42
    while True:
        event_id = check_recent_sales(api, event_id)
        logger.info("Waiting...")
        time.sleep(60)


if __name__ == "__main__":
    main()
