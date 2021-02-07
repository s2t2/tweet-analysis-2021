

import os

from dotenv import load_dotenv
from tweepy import OAuthHandler, API, Cursor, TweepError

from helpers.number_decorators import fmt_n

load_dotenv()

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", default="OOPS")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET", default="OOPS")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", default="OOPS")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", default="OOPS")


class TwitterService:
    def __init__(self, api_key=TWITTER_API_KEY, api_key_secret=TWITTER_API_KEY_SECRET,
                        access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET):
        """Docs:
            https://docs.tweepy.org/en/latest/getting_started.html
            https://docs.tweepy.org/en/latest/api.html
        """
        auth = OAuthHandler(api_key, api_key_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_user(self, screen_name):
        return self.api.get_user(screen_name)

    def get_statuses(self, request_params={}, limit=2_000):
        """See:
            https://docs.tweepy.org/en/latest/api.html#timeline-methods
            https://docs.tweepy.org/en/v3.10.0/cursor_tutorial.html

        Params:
            request_params (dict) needs either "user_id" or "screen_name" attr

            limit (int) the number of total tweets to fetch per user

        Example: get_statuses({"user_id": 10101, "count": 100}, limit=300)
        """
        default_params = {
            "exclude_replies": False,
            "include_rts": True,
            "tweet_mode": "extended",
            "count": 200 # number of tweets per request
        }
        request_params = {**default_params, **request_params} # use the defaults, and override with user-specified params (including the required user_id or screen_name)
        request_params["cursor"] = -1 # use a cursor approach!

        cursor = Cursor(self.api.user_timeline, **request_params)
        #return cursor.pages()
        return cursor.items(limit)


if __name__ == "__main__":
    from pprint import pprint

    twitter_service = TwitterService()

    screen_name = os.getenv("SCREEN_NAME", default="barackobama")

    user = twitter_service.get_user(screen_name)
    #pprint(user._json)
    print("----------------")
    print("USER:", screen_name.upper())
    print("FOLLOWERS:", fmt_n(user.followers_count))
    print("FRIENDS:", fmt_n(user.friends_count))
    print("STATUSES:", fmt_n(user.statuses_count))
    print("LISTED:", fmt_n(user.listed_count))
    try:
        print("LATEST_STATUS:", user.status.id, user.status.text)
    except:
        pass

    print("----------------")
    print("TIMELINE:")
    counter = 0
    for status in twitter_service.get_statuses(request_params={"screen_name":screen_name, "count":10}, limit=25):
        counter +=1
        print("----------------")
        print(counter, status.full_text)
