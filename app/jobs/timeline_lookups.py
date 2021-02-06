

import os
from time import sleep
#from functools import lru_cache
from dotenv import load_dotenv
from tqdm import tqdm as progress_bar

from app import seek_confirmation
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import TwitterService
from app.tweet_parser import parse_timeline_status

load_dotenv()

DATASET_ADDRESS = os.getenv("DATASET_ADDRESS", default="tweet-collector-py.disinfo_2021_development")
USER_LIMIT = int(os.getenv("USER_LIMIT", default="100"))
STATUS_LIMIT = int(os.getenv("STATUS_LIMIT", default="5_000"))


#lass TimelineLookupsJob():
#   def __init__(self, bq_service=None, twitter_service=None, dataset_address=DATASET_ADDRESS,
#                                               user_limit=USER_LIMIT, status_limit=STATUS_LIMIT):
#       self.bq_service = bq_service or BigQueryService()
#       self.twitter_service = twitter_service or TwitterService()
#
#       # consider stripping dataset_address of semicolons, just in case, for SQL injection reasons
#       # there is a way to pass safe params from users to bq but we don't anticipate users setting the DATASET_ADDRESS env var, which is why SQL injection is less of a concern
#       self.dataset_address = dataset_address
#       self.user_limit = user_limit
#       self.status_limit = status_limit
#
#       #self.parse_status = parse_timeline_status
#
#   def fetch_users(self):
#       sql = f"""
#           WITH user_lookups as (
#               SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
#               FROM `{self.dataset_address}.user_lookups`
#           )
#
#           SELECT DISTINCT ul.user_id
#           FROM user_lookups ul
#           LEFT JOIN `{self.dataset_address}.timeline_lookups` tl ON tl.user_id = ul.user_id
#           WHERE ul.error_code IS NULL
#               AND ul.status_count > 0
#               AND tl.user_id IS NULL
#           LIMIT {USER_LIMIT};
#       """
#       #print(sql)
#       return [row["user_id"] for row in list(self.bq_service.execute_query(sql))]
#
#   @property
#   @lru_cache(maxsize=None)
#   def lookups_table(self):
#       return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_lookups")
#
#   @property
#   @lru_cache(maxsize=None)
#   def timelines_table(self):
#       return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_tweets")
#
#   def fetch_statuses(self, user_id):
#       return self.twitter_service.get_statuses(user_id=user_id, limit=self.statuses_limit)
#
#   def save_timeline(self, timeline):
#       self.bq_service.insert_records_in_batches(records=timeline, table=self.timelines_table)
#
#   def save_lookups(self, lookups):
#       self.bq_service.insert_records_in_batches(records=lookups, table=self.lookups_table)


if __name__ == '__main__':

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    print("DATASET:", DATASET_ADDRESS.upper())
    print("USER LIMIT:", USER_LIMIT)
    print("STATUS LIMIT:", STATUS_LIMIT)

    seek_confirmation()

    #
    # GET USERS, EXCLUDING THOSE WHO ARE: SUSPENDED, NOT FOUND, PREVIOUSLY LOOKED-UP
    #

    sql = f"""
        WITH user_lookups as (
            SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
            FROM `{DATASET_ADDRESS}.user_lookups`
        )

        SELECT DISTINCT ul.user_id
        FROM user_lookups ul
        LEFT JOIN `{DATASET_ADDRESS}.timeline_lookups` tl ON tl.user_id = ul.user_id
        WHERE ul.error_code IS NULL
            AND ul.status_count > 0
            AND tl.user_id IS NULL
        LIMIT {USER_LIMIT};
    """
    #print(sql)
    user_ids = [row["user_id"] for row in list(bq_service.execute_query(sql))]

    print("USERS:", len(user_ids))
    if not any(user_ids):
        print("SLEEPING...")
        sleep(10 * 60 * 60)
        exit()

    #
    # GET TIMELINE TWEETS FOR EACH USER
    #

    lookups_table = bq_service.client.get_table(f"{DATASET_ADDRESS}.timeline_lookups")
    timelines_table = bq_service.client.get_table(f"{DATASET_ADDRESS}.timeline_tweets")

    lookups = []
    for index, user_id in enumerate(user_ids):
        print("---------------------")
        print("USER ID:", index, user_id)

        timeline = []
        lookup = {
            "user_id": user_id,
            "error_code": None, "error_type": None, "error_message": None,
            "timeline_length": None #, "timeline_start": None, "timeline_end": None
        }

        try:
            for status in progress_bar(twitter_service.get_statuses(user_id=user_id, limit=STATUS_LIMIT), total=STATUS_LIMIT):
                timeline.append(parse_timeline_status(status))

            lookup["timeline_length"] = len(timeline)
            lookup["message"] = "SUCCESS"

        except Exception as err:
            #print("OOPS", err)
            if hasattr(err, "api_code"):
                lookup["error_code"] = err.api_code
            lookup["error_type"] = type(err)
            lookup["message"] = err.reason or str(err)

        print(lookup)
        lookups.append(lookup)

        if any(timeline):
            bq_service.insert_records_in_batches(records=timeline, table=timelines_table)

    if any(lookups):
        # TODO: ensure there aren't any situations where
        # ... the timeline gets saved above, but the lookup record does not get saved below
        # ... (like in the case of an unexpected error or something)
        bq_service.insert_records_in_batches(records=lookups, table=lookups_table)
