

import os
from time import sleep
from dotenv import load_dotenv

from app import seek_confirmation
from app.bq_service import BigQueryService, generate_timestamp
from app.twitter_service import TwitterService
from app.tweet_parser import parse_timeline_status

load_dotenv()

DATASET_ADDRESS = os.getenv("DATASET_ADDRESS", default="tweet-collector-py.disinfo_2021_development")
USER_LIMIT = int(os.getenv("USER_LIMIT", default="10")) # 3
STATUS_LIMIT = int(os.getenv("STATUS_LIMIT", default="1_000")) # 10


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
    for user_id in user_ids:
        print("---------------------")
        print("USER ID:", user_id)

        timeline = []
        lookup = {
            "user_id": user_id,
            "error_code": None, "error_type": None, "error_message": None,
            "timeline_length": None #, "timeline_start": None, "timeline_end": None
        }

        try:
            for status in twitter_service.get_statuses(user_id=user_id, limit=STATUS_LIMIT):
                timeline.append(parse_timeline_status(status))
            lookup["timeline_length"] = len(timeline)
        except Exception as err:
            #print("OOPS", err)
            #lookup["error_code"] = err.api_code # theoretically
            lookup["error_type"] = type(err)
            lookup["error_message"] = err.reason

        print(lookup)
        lookups.append(lookup)

        if any(timeline):
            bq_service.insert_records_in_batches(records=timeline, table=timelines_table)

    if any(lookups):
        bq_service.insert_records_in_batches(records=lookups, table=lookups_table)
