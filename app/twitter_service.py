

import os
from dotenv import load_dotenv

from helpers.number_decorators import fmt_n

load_dotenv()

################################

from tweepy import OAuthHandler, API, Cursor, TweepError

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

    def get_tweets(self, screen_name):
        return self.api.user_timeline(screen_name,
            tweet_mode="extended",
            #count=150,
            exclude_replies=True,
            include_rts=False
        )

    def get_statuses(self, screen_name=None, user_id=None, limit=2000):
        """See:
            https://docs.tweepy.org/en/latest/api.html#timeline-methods
            https://docs.tweepy.org/en/v3.10.0/cursor_tutorial.html
        """
        request_params = {"cursor": -1, "exclude_replies": False, "include_rts": True}
        if user_id:
            request_params["user_id"] = user_id
        elif screen_name:
            request_params["screen_name"] = screen_name

        cursor = Cursor(self.api.user_timeline, **request_params)
        return cursor.items(limit)
        #return cursor.pages()


if __name__ == "__main__":
    from pprint import pprint

    twitter_service = TwitterService()

    screen_name = "barackobama"

    user = twitter_service.get_user(screen_name)
    #pprint(user._json)
    print("USER:", screen_name.upper())
    print("FOLLOWERS:", fmt_n(user.followers_count))
    print("FRIENDS:", fmt_n(user.friends_count))
    print("STATUSES:", fmt_n(user.statuses_count))
    print("LISTED:", fmt_n(user.listed_count))
    try:
        print("LATEST_STATUS:", user.status.id, user.status.text)
    except:
        pass

    #counter = 1
    #for status in twitter_service.get_statuses(screen_name):
    #    print("----------------")
    #    print(counter, status)
    #    counter+=1
    #    #if counter >= 100: break

    #print("GET STATUSES:", len(list(twitter_service.get_statuses(screen_name))))
