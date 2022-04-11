
import os
#from pprint import pprint
from functools import lru_cache

from dotenv import load_dotenv

from app import seek_confirmation, server_sleep
from app.bq_service import BigQueryService, split_into_batches, generate_timestamp
from app.twitter_service import TwitterService
from app.tweet_recollection.parser import parse_full_text

load_dotenv()

STATUS_LIMIT = int(os.getenv("STATUS_LIMIT", default="100_000")) # number of ids to fetch from BQ
BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="100")) # must be less than 100

ANALYSIS_DATASET_ADDRESS = os.getenv("ANALYSIS_DATASET_ADDRESS", default="tweet-collector-py.analysis_2021_development")

class Collector:
    """
    This requires some table setup... see MIGRATIONS.md file in this directory for more info.
    """

    def __init__(self):
        self.twitter_api = TwitterService().api
        self.bq_service = BigQueryService()
        self.limit = STATUS_LIMIT
        self.batch_size = BATCH_SIZE
        self.analysis_dataset_address = ANALYSIS_DATASET_ADDRESS

    def perform(self):
        remaining_status_ids = self.fetch_remaining_status_ids()
        if any(remaining_status_ids):
            for batch_of_ids in split_into_batches(remaining_status_ids, batch_size=self.batch_size):
                self.process_batch(batch_of_ids)
        else:
            print("OH ALL DONE! SLEEPING...")
            server_sleep(10*60*60)

    def fetch_remaining_status_ids(self):
        """
        For this pass we will do the 33M stream listener tweets.
        If you want to look up the timeline tweets, make a new class and override this method to fetch them instead.
        """

        sql = f"""
            WITH all_statuses as (
                SELECT DISTINCT status_id
                FROM `{self.analysis_dataset_address}.all_status_ids` -- 765,966,689
                WHERE impeachment_2020=0 and disinfo_timeline=0 -- 33,508,881
            )

            SELECT DISTINCT all_statuses.status_id
            FROM all_statuses
            LEFT JOIN `{self.analysis_dataset_address}.recollected_statuses` completed ON completed.status_id = all_statuses.status_id
            WHERE completed.status_id IS NULL
            LIMIT {self.limit}
        """
        return [row["status_id"] for row in list(self.bq_service.execute_query(sql))]

    def process_batch(self, status_ids):
        recollected_statuses = []
        recollected_urls = []
        success_counter = 0
        for status in self.lookup_statuses(status_ids):
            # when passing param map_=True to Twitter API, if statuses are not available, the status will be present, but will only have an id field
            status_id = status.id # all statuses will have an id

            recollected_status = {
                "status_id": status_id,
                "user_id": None,
                "full_text": None,
                "created_at": None,
                "lookup_at": generate_timestamp()
            } # represent failed lookups with null text values
            if list(status._json.keys()) != ["id"]: # this will be the only field for empty statuses. otherwise try to parse them:
                success_counter+=1
                recollected_status["user_id"] = status.user.id
                recollected_status["full_text"] = parse_full_text(status) # update the full text if possible
                recollected_status["created_at"] = generate_timestamp(status.created_at)
                for url in status.entities["urls"]:
                    recollected_urls.append({"status_id": status_id, "expanded_url": url["expanded_url"]})
            recollected_statuses.append(recollected_status)

        print(generate_timestamp(), f"| SAVING BATCH OF {len(status_ids)}", "| STATUSES:", success_counter, "| URLS:", len(recollected_urls))
        self.save_statuses(recollected_statuses)
        self.save_urls(recollected_urls)

    def lookup_statuses(self, status_ids):
        """Fetch full status info including urls, and full text.
            Max per request is 100, so batch size must be smaller than that.
            See:
                https://docs.tweepy.org/en/stable/api.html#API.statuses_lookup
                https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup
        """
        return self.twitter_api.statuses_lookup(
            id_=status_ids,
            include_entities=True, # this is where the full urls are
            trim_user=True, # we already have this info
            include_ext_alt_text=True, # If alt text has been added to any attached media entities, this parameter will return an ext_alt_text value in the top-level key for the media entity. If no value has been set, this will be returned as null.
            include_card_uri=False,
            map_=True, # "Tweets that do not exist or cannot be viewed by the current user will still have their key represented but with an explicitly null value paired with it"

            tweet_mode="extended"
        )

    def save_statuses(self, recollected_statuses):
        self.bq_service.insert_records_in_batches(self.recollected_statuses_table, recollected_statuses)

    def save_urls(self, recollected_urls):
        self.bq_service.insert_records_in_batches(self.recollected_urls_table, recollected_urls)

    @property
    @lru_cache(maxsize=None)
    def recollected_statuses_table(self):
        return self.bq_service.client.get_table(f"{self.analysis_dataset_address}.recollected_statuses")

    @property
    @lru_cache(maxsize=None)
    def recollected_urls_table(self):
        return self.bq_service.client.get_table(f"{self.analysis_dataset_address}.recollected_status_urls")




if __name__ == '__main__':

    collector = Collector()

    print("LIMIT:", collector.limit)
    print("BATCH SIZE:", collector.batch_size)

    seek_confirmation()

    collector.perform()
