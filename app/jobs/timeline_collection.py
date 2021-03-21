

import os
from time import sleep
from functools import lru_cache
from dotenv import load_dotenv
#from tqdm import tqdm as progress_bar

from app import seek_confirmation, APP_ENV
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import TwitterService
from app.tweet_parser import parse_timeline_status

load_dotenv()

USER_LIMIT = os.getenv("USER_LIMIT", default="100_000")
STATUS_LIMIT = os.getenv("STATUS_LIMIT", default="100_000")


class TimelineCollectionJob():
    def __init__(self, bq_service=None, twitter_service=None, user_limit=USER_LIMIT, status_limit=STATUS_LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.twitter_service = twitter_service or TwitterService()

        self.dataset_address = self.bq_service.dataset_address
        self.user_limit = int(user_limit)
        self.status_limit = int(status_limit)

        self.parse_status = parse_timeline_status

        print("---------------------------")
        print("JOB: TIMELINE LOOKUPS")
        print("DATASET:", self.dataset_address.upper())
        print("USER LIMIT:", self.user_limit)
        print("STATUS LIMIT:", self.status_limit)
        print("---------------------------")

    def fetch_users(self):
        sql = f"""
            SELECT
                all_users.user_id
                ,all_users.status_count
                ,all_users.first_status_at
                ,prev_lookups.latest_status_id
                ,prev_lookups.latest_lookup_at
            FROM (
                SELECT
                    cast(user_id as int64) as user_id
                    ,count(distinct status_id) as status_count
                    ,min(created_at) first_status_at
                FROM `{self.dataset_address}.tweets`
                GROUP BY 1
            ) all_users
            LEFT JOIN (
                SELECT
                    user_id
                    ,max(status_id) as latest_status_id
                    ,max(lookup_at) latest_lookup_at
                FROM `{self.dataset_address}.timeline_tweets`
                GROUP BY 1
            ) prev_lookups ON all_users.user_id = prev_lookups.user_id
            LEFT JOIN (
                -- inactive users (suspended or not found)
                SELECT DISTINCT cast(user_id as int64) as user_id
                FROM `{self.dataset_address}.user_lookups`
                WHERE error_code = 50 OR error_code = 63
            ) inactive_users ON inactive_users.user_id = all_users.user_id
            WHERE inactive_users.user_id IS NULL -- exclude inactive users -- 410,390 vs 440,211
            ORDER BY latest_lookup_at
            LIMIT {self.user_limit};
        """
        #print(sql)
        return list(self.bq_service.execute_query(sql))

    def fetch_statuses(self, user_id, latest_status_id=None):
        return self.twitter_service.get_statuses(
            request_params={"user_id": user_id, "since_id": latest_status_id},
            limit=self.status_limit
        )

    def save_timeline(self, timeline):
        return self.bq_service.insert_records_in_batches(records=timeline, table=self.timelines_table)

    def save_lookups(self, lookups):
        return self.bq_service.insert_records_in_batches(records=lookups, table=self.lookups_table)

    @property
    @lru_cache(maxsize=None)
    def lookups_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_lookups")

    @property
    @lru_cache(maxsize=None)
    def timelines_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_tweets")


if __name__ == '__main__':
    from pprint import pprint

    job = TimelineCollectionJob()

    seek_confirmation()

    #
    # GET USERS, EXCLUDING THOSE WHO ARE: SUSPENDED, NOT FOUND, PREVIOUSLY LOOKED-UP
    #

    users = job.fetch_users()
    print("USERS:", len(users))
    if not any(users):
        print("SLEEPING...")
        sleep(10 * 60 * 60) # let the server rest while we have time to shut it down
        exit() # don't try to do more work


    lookups = []
    try:

        #
        # GET TIMELINE TWEETS FOR EACH USER
        #

        for index, row in enumerate(users):
            user_id = row["user_id"]
            latest_status_id = row["latest_status_id"]
            print("---------------------")
            print("USER ID:", index, user_id, "LATEST STATUS:", latest_status_id)

            lookup = {
                "user_id": user_id,
                "timeline_length": None,
                "error_type": None,
                "error_message": None,
                "start_at": generate_timestamp(),
                "end_at": None
            }
            timeline = []

            try:
                for status in job.fetch_statuses(user_id=user_id, latest_status_id=latest_status_id):
                    timeline.append(job.parse_status(status))

                lookup["timeline_length"] = len(timeline)
            except Exception as err:
                lookup["error_type"] = err.__class__.__name__
                lookup["error_message"] = str(err)
            lookup["end_at"] = generate_timestamp()
            print(lookup)
            lookups.append(lookup)

            if any(timeline):
                print("SAVING", len(timeline), "TIMELINE TWEETS...")
                errors = job.save_timeline(timeline)
                if errors:
                    pprint(errors)
                    #breakpoint()

    finally:
        # ensure there aren't any situations where
        # ... the timeline gets saved above, but the lookup record does not get saved below
        # ... (like in the case of an unexpected error or something)
        if any(lookups):
            print("SAVING", len(lookups), "LOOKUPS...")
            errors = job.save_lookups(lookups)
            if errors:
                pprint(errors)
                #breakpoint()

    print("JOB COMPLETE!")

    if APP_ENV == "production":
        print("SLEEPING...")
        sleep(3 * 24 * 60 * 60) # let the server rest while we have time to shut it down
