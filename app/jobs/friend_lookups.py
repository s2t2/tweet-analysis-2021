

import os
from time import sleep
from functools import lru_cache
from dotenv import load_dotenv
from tqdm import tqdm as progress_bar

from app import seek_confirmation
from app.bq_service import BigQueryService, generate_timestamp, DATASET_ADDRESS
from app.twitter_service import TwitterService
from app.tweet_parser import parse_timeline_status

load_dotenv()

USER_LIMIT = os.getenv("USER_LIMIT", default="250")
FRIEND_LIMIT = os.getenv("FRIEND_LIMIT", default="10_000")


class FriendLookupsJob():
    def __init__(self, bq_service=None, twitter_service=None, user_limit=USER_LIMIT, friend_limit=FRIEND_LIMIT):
        self.bq_service = bq_service or BigQueryService()
        self.twitter_service = twitter_service or TwitterService()

        self.dataset_address = self.bq_service.dataset_address
        self.user_limit = int(user_limit)
        self.friend_limit = int(friend_limit)

        print("---------------------------")
        print("JOB: FRIEND LOOKUPS")
        print("DATASET:", self.dataset_address.upper())
        print("USER LIMIT:", self.user_limit)
        print("FRIEND LIMIT:", self.friend_limit)
        print("---------------------------")

    def fetch_users(self):
        sql = f"""
            WITH user_lookups as (
                SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
                FROM `{self.dataset_address}.user_lookups`
                WHERE error_code IS NULL and friend_count > 0
                --LIMIT 10
            )

            SELECT DISTINCT ul.user_id
            FROM user_lookups ul
            LEFT JOIN `{self.dataset_address}.friend_lookups` fl ON fl.user_id = ul.user_id
            WHERE fl.user_id IS NULL -- only users that have not yet been looked up
            LIMIT {self.user_limit};
        """
        #print(sql)
        return [row["user_id"] for row in list(self.bq_service.execute_query(sql))]

    #def fetch_friends(self, user_id):
    #    return self.twitter_service.get_friends(request_params={"user_id": user_id}, limit=self.friend_limit)

    def save_friends(self, user_friends):
        return self.bq_service.insert_records_in_batches(records=user_friends, table=self.friends_table)

    def save_lookups(self, lookups):
        return self.bq_service.insert_records_in_batches(records=lookups, table=self.lookups_table)

    @property
    @lru_cache(maxsize=None)
    def lookups_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.friend_lookups")

    @property
    @lru_cache(maxsize=None)
    def friends_table(self):
        return self.bq_service.client.get_table(f"{self.dataset_address}.friends")


if __name__ == '__main__':
    from pprint import pprint

    job = FriendLookupsJob()

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

    lookups = []
    try:

        #
        # GET FRIENDS FOR EACH USER
        #

        for index, user_id in enumerate(user_ids):
            print("---------------------")
            print("USER ID:", index, user_id)

            lookup = {
                "user_id": user_id,
                "friend_count": None,
                "error_type": None,
                "error_message": None,
                "start_at": generate_timestamp(),
                "end_at": None
            }
            friends = []

            try:

                for friend in job.twitter_service.get_friends(request_params={"user_id": user_id}, limit=job.friend_limit):
                    friends.append({
                        "user_id": user_id,
                        "friend_id": friend.id, # friend.id_str
                        "friend_name": friend.screen_name.upper(),
                        "lookup_at": generate_timestamp(),
                    })

                lookup["friend_count"] = len(friends)
            except Exception as err:
                lookup["error_type"] = err.__class__.__name__
                lookup["error_message"] = str(err)
            lookup["end_at"] = generate_timestamp()
            print(lookup)
            lookups.append(lookup)

            if any(friends):
                print("SAVING", len(friends), "FRIENDS...")
                errors = job.save_friends(friends)
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
