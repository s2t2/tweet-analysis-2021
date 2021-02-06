

import os
from time import sleep
from functools import lru_cache
from dotenv import load_dotenv
from tqdm import tqdm as progress_bar

from app import seek_confirmation
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import TwitterService
from app.tweet_parser import parse_timeline_status

load_dotenv()

DATASET_ADDRESS = os.getenv("DATASET_ADDRESS", default="tweet-collector-py.disinfo_2021_development")
USER_LIMIT = os.getenv("USER_LIMIT", default="500")
STATUS_LIMIT = os.getenv("STATUS_LIMIT", default="10_000")


class TimelineLookupsJob():
    def __init__(self, bq_service=None, twitter_service=None, dataset_address=DATASET_ADDRESS,
                                        user_limit=USER_LIMIT, status_limit=STATUS_LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.twitter_service = twitter_service or TwitterService()

        self.dataset_address = dataset_address.replace(";", "") # stripping dataset_address of semicolons, just in case, for SQL injection reasons, even though we don't we don't anticipate external users setting the DATASET_ADDRESS env var
        self.user_limit = int(user_limit)
        self.status_limit = int(status_limit)

        #self.parse_status = parse_timeline_status

        print("---------------------------")
        print("JOB: TIMELINE LOOKUPS")
        print("DATASET:", self.dataset_address.upper())
        print("USER LIMIT:", self.user_limit)
        print("STATUS LIMIT:", self.status_limit)
        print("---------------------------")

    def fetch_users(self):
        sql = f"""
            WITH user_lookups as (
                SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
                FROM `{self.dataset_address}.user_lookups`
            )

            SELECT DISTINCT ul.user_id
            FROM user_lookups ul
            LEFT JOIN `{self.dataset_address}.timeline_lookups` tl ON tl.user_id = ul.user_id
            WHERE ul.error_code IS NULL
                AND ul.status_count > 0
                AND tl.user_id IS NULL
            LIMIT {self.user_limit};
        """
        #print(sql)
        return [row["user_id"] for row in list(self.bq_service.execute_query(sql))]

    @property
    @lru_cache(maxsize=None)
    def lookups_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_lookups")

    @property
    @lru_cache(maxsize=None)
    def timelines_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.timeline_tweets")

    def fetch_statuses(self, user_id):
        return self.twitter_service.get_statuses(user_id=user_id, limit=self.status_limit)

    def save_timeline(self, timeline):
        self.bq_service.insert_records_in_batches(records=timeline, table=self.timelines_table)

    def save_lookups(self, lookups):
        self.bq_service.insert_records_in_batches(records=lookups, table=self.lookups_table)


if __name__ == '__main__':

    job = TimelineLookupsJob()

    seek_confirmation()

    #
    # GET USERS, EXCLUDING THOSE WHO ARE: SUSPENDED, NOT FOUND, PREVIOUSLY LOOKED-UP
    #

    user_ids = job.fetch_users()
    print("USERS:", len(user_ids))
    if not any(user_ids):
        print("SLEEPING...")
        sleep(10 * 60 * 60) # let the server rest while we have time to shut it down
        exit() # don't try to do more work

    #
    # GET TIMELINE TWEETS FOR EACH USER
    #

    lookups = []
    try:

        for index, user_id in enumerate(user_ids):
            print("---------------------")
            print("USER ID:", index, user_id)

            timeline = []
            lookup = {"user_id": user_id, "timeline_length": None, "error_code": None, "error_type": None, "error_message": None}
            try:
                for status in progress_bar(job.fetch_statuses(user_id=user_id), total=job.status_limit):
                    timeline.append(parse_timeline_status(status))
                lookup["timeline_length"] = len(timeline)
            except Exception as err:
                #print("OOPS", err)
                lookup["error_type"] = err.__class__.__name__

                #if hasattr(err, "reason"):
                #    lookup["error_message"] = err.reason
                #else:
                #    lookup["error_message"] = str(err)
                lookup["error_message"] = str(err)

                if hasattr(err, "api_code"):
                    lookup["error_code"] = err.api_code


            print(lookup)
            lookups.append(lookup)

            if any(timeline):
                job.save_timeline(timeline)

    finally:
        # use this try, finally to ensure there aren't any situations where
        # ... the timeline gets saved above, but the lookup record does not get saved below
        # ... (like in the case of an unexpected error or something)
        # ... sending an API request to BQ to store a single lookup record feels bad, so...
        if any(lookups):
            print("SAVING", len(lookups), "LOOKUPS...")
            job.save_lookups(lookups)

    print("JOB COMPLETE!")
