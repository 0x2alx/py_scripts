# -*- coding: utf-8 -*-
# https://realpython.com/twitter-bot-python-tweepy/#creating-twitter-api-authentication-credentials
import logging
import os

import tweepy
from dotenv import load_dotenv

logger = logging.getLogger()
load_dotenv()


def create_api():
    consumer_key = os.getenv("API_KEY")
    consumer_secret = os.getenv("API_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("BEARER_TOKEN")
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, timeout=120, retry_count=3)
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
        wait_on_rate_limit=True,
    )
    """
    #auth = tweepy.OAuth2BearerHandler(bearer_token)
    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    api = tweepy.API(auth)

    client = tweepy.Client(bearer_token=bearer_token)

    # If the authentication was successful, this should print the
    # screen name / username of the account
    print(api.verify_credentials().screen_name)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api, client


if __name__ == "__main__":
    print("main")
    create_api()
