

from tweepy.error import TweepError

from helpers.bq_service import BigQueryService
from helpers.twitter_service import TwitterService

if __name__ == "main":

    bq_service = BigQueryService()
    twitter_service = TwitterService()

    limit = 5_000
    term = "#WWG1WGA"

    sql = f"""
        WITH users as (
            SELECT
                t.user_id
                ,string_agg(distinct upper(t.user_screen_name), ', ') as screen_names
                ,any_value(t.user_verified) as user_verified
                ,extract(date from any_value(t.user_created_at)) as user_created_on
                ,count(distinct t.status_id) as status_count
            FROM `tweet-research-shared.disinfo_2021.tweets_view` t
            WHERE REGEXP_CONTAINS(upper(status_text), '{term}')
            GROUP BY 1
            ORDER BY status_count desc
        )

        SELECT
            u.*
            --,ul.user_id as lookup_user_id
        FROM users u
        LEFT JOIN `tweet-research-shared.disinfo_2021.user_lookups` ul ON ul.user_id = u.user_id
            AND ul.user_id is null -- skip previously looked up users
        ORDER BY status_count desc
    """
    if limit:
        sql += f" LIMIT {limit} "

    users_df = bq_service.query_to_df(sql)
    print(users_df.head())

    records = []

    for index, row in users_df.iterrows():
        #print(index, dict(row))
        #if index >=5: break

        record = {
            "user_id": row["user_id"],
            "error_code": None,
            "follower_count": None,
            "friend_count": None,
            "listed_count": None,
            "status_count": None,
            "latest_status_id": None
        }
        try:
            user = twitter_service.get_user(row["user_id"])
            record["follower_count"] = user.followers_count
            record["friend_count"] = user.friends_count
            record["listed_count"] = user.listed_count
            record["status_count"] = user.statuses_count
            try:
                # 'User' object has no attribute 'status'
                record["latest_status_id"] = user.status.id
            except:
                pass
        except TweepError as err:
            #breakpoint()
            #zzz = err # cache for later / attempts to parse the reason attribute. its ok we can look up the code here:
            # https://developer.twitter.com/ja/docs/basics/response-codes
            # 63 means user has been suspended, etc.
            record["error_code"] = err.api_code

        print(index, record)
        records.append(record)
