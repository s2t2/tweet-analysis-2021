

import os

#from tweepy.error import TweepError

#from app import APP_ENV
from app.bq_service import BigQueryService
from app.twitter_service import TwitterService

STATUS_LIMIT = int(os.getenv("LIMIT", default="10_000"))

#def process_batch():
#    #timelines_table = bq_service.client.get_table("tweet-research-shared.disinfo_2021.timelines")
#    #bq_service.insert_records_in_batches(records=timeline, table=timelines_table)


if __name__ == '__main__':

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    # get timeline for each user
    # ... excluding users suspended or not found during the lookup process
    sql = f"""
        SELECT DISTINCT user_id
        FROM `tweet-research-shared.disinfo_2021.user_lookups`
        WHERE error_code IS NULL AND status_count > 0
    """
    results_df = bq_service.query_to_df(sql)
    user_ids = results_df["user_id"].tolist()
    print(len(user_ids))

    #lookups_table = bq_service.client.get_table("tweet-research-shared.disinfo_2021.timeline_lookups")
    timelines_table = bq_service.client.get_table("tweet-research-shared.disinfo_2021.timelines")

    for user_id in user_ids:
        # TODO: use threadpool executor, return user_id "as completed"
        print("FETCHING TIMELINE FOR :", user_id)

        timeline = []
        for status in twitter_service.get_statuses(user_id, limit=STATUS_LIMIT):
            breakpoint()
            record = status._json
            timeline.append(record)

            if len(timeline) >= BATCH_SIZE:
                bq_service.insert_records_in_batches(records=timeline, table=timelines_table)
                batch = []

        if any(timeline):
            bq_service.insert_records_in_batches(records=timeline, table=timelines_table)
            batch = []




















        #lookups_table = bq_service.client.get_table("tweet-research-shared.disinfo_2021.timeline_lookups")
        #bq_service.insert_records_in_batches(records=lookups, table=lookups_table)
