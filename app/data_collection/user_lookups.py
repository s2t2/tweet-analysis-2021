

import os
from dotenv import load_dotenv
from tweepy.error import TweepError

from app import APP_ENV, seek_confirmation
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService

load_dotenv()

DATASET_ADDRESS = os.getenv("DATASET_ADDRESS", default="tweet-collector-py.disinfo_2021_development")
SEARCH_TERM = os.getenv("SEARCH_TERM", default="#WWG1WGA")
LIMIT = os.getenv("LIMIT") # None is OK

#class UserLookupJob:
#    def __init__(self):
#        pass

if __name__ == '__main__':

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    print("SEARCH_TERM:", SEARCH_TERM)
    print("LIMIT:", LIMIT)
    print(bq_service.query_to_df(f"SELECT count(distinct user_id) FROM `{DATASET_ADDRESS}.user_lookups`"))

    seek_confirmation()

    sql = f"""
        SELECT DISTINCT u.user_id
        FROM (
            SELECT DISTINCT cast(user_id as INT64) as user_id
            FROM `{DATASET_ADDRESS}.tweets`
            WHERE REGEXP_CONTAINS(upper(status_text), '{SEARCH_TERM}')
        ) u
        LEFT JOIN (
            SELECT DISTINCT user_id
            FROM `{DATASET_ADDRESS}.user_lookups`
        ) ul ON ul.user_id = u.user_id
        WHERE ul.user_id IS NULL -- exclude users with existing look-ups
    """
    if LIMIT:
        sql += f" LIMIT {int(LIMIT)} "
    #print(sql)

    results_df = bq_service.query_to_df(sql)
    print(results_df.head())

    lookups = []
    for index, row in results_df.iterrows():
        # construct a record to insert into the lookups table. need to convert numpy.int64 to normal int
        lookup = {
            "user_id": int(row["user_id"]),
            "error_code": None,
            "follower_count": None,
            "friend_count": None,
            "listed_count": None,
            "status_count": None,
            "latest_status_id": None
        }
        try:
            user = twitter_service.get_user(row["user_id"])
            lookup["follower_count"] = int(user.followers_count)
            lookup["friend_count"] = int(user.friends_count)
            lookup["listed_count"] = int(user.listed_count)
            lookup["status_count"] = int(user.statuses_count)
            try:
                # it is possible that... 'User' object has no attribute 'status'
                lookup["latest_status_id"] = int(user.status.id)
            except:
                pass
        except TweepError as err:
            # see: https://developer.twitter.com/ja/docs/basics/response-codes
            # ... 63 means user has been suspended, etc.
            lookup["error_code"] = err.api_code

        print(index, lookup)
        lookups.append(lookup)

    table = bq_service.client.get_table(f"{DATASET_ADDRESS}.user_lookups")
    bq_service.insert_records_in_batches(records=lookups, table=table)

    print(bq_service.query_to_df(f"SELECT count(distinct user_id) FROM `{DATASET_ADDRESS}.user_lookups`"))

    print("JOB COMPLETE...")

    if APP_ENV=="production":
        print("SLEEPING...")
        sleep(10 * 60 * 60) # let the server rest while we have time to shut it down
        exit() # don't try to do more work
