

import os

from tweepy.error import TweepError

from app import APP_ENV
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService

SEARCH_TERM = os.getenv("SEARCH_TERM", default="#MySearchTerm")
LIMIT = os.getenv("LIMIT") # None is OK

if __name__ == '__main__':

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    print("SEARCH_TERM:", SEARCH_TERM)
    print("LIMIT:", LIMIT)
    print(bq_service.query_to_df("""
            SELECT count(distinct user_id)
            FROM `tweet-research-shared.disinfo_2021.user_lookups`
        """))

    if APP_ENV=="development" and input("CONTINUE? (Y/N): ").upper() != "Y":
        print("EXITING...")
        exit()

    sql = f"""
        SELECT DISTINCT u.user_id
        FROM (
            SELECT DISTINCT user_id
            FROM `tweet-research-shared.disinfo_2021.tweets_view`
            WHERE REGEXP_CONTAINS(upper(status_text), '{SEARCH_TERM}')
        ) u
        LEFT JOIN (
            SELECT DISTINCT user_id
            FROM `tweet-research-shared.disinfo_2021.user_lookups`
        ) ul ON ul.user_id = u.user_id
        WHERE ul.user_id IS NULL -- exclude users with existing look-ups
    """
    if LIMIT:
        sql += f" LIMIT {int(LIMIT)} "

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

    table = bq_service.client.get_table("tweet-research-shared.disinfo_2021.user_lookups")
    bq_service.insert_records_in_batches(records=lookups, table=table)

    print(bq_service.query_to_df("""
        SELECT count(distinct user_id)
        FROM `tweet-research-shared.disinfo_2021.user_lookups`
    """))

    print("JOB COMPLETE. RESTARTING...")
