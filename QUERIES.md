
# Data Prep and Cleaning

## Tweets v2

The `tweets_v2` tables cast ids as integers. This will make for faster joins in the future on these columns.

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.election_2020_production.tweets_v2`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.election_2020_production.tweets_v2` as (
    SELECT
        cast(status_id as int64) as status_id
        ,status_text
        ,truncated
        ,is_quote
        ,geo
        ,created_at

        ,cast(retweeted_status_id as int64) as retweeted_status_id
        ,cast(retweeted_user_id as int64) as retweeted_user_id
        ,retweeted_user_screen_name

        ,cast(reply_status_id as int64) as reply_status_id
        ,cast(reply_user_id as int64) as reply_user_id

        ,cast(user_id as int64) as user_id
        ,user_name
        ,user_screen_name
        ,user_description
        ,user_location
        ,user_verified
        ,user_created_at

    FROM  `tweet-collector-py.election_2020_production.tweets`
    --LIMIT 10
)
```


```sql
-- DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.tweets_v2`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.tweets_v2` as (
    SELECT
        -- ...
    FROM  `tweet-collector-py.disinfo_2021_production.tweets`
    --LIMIT 10
)
```

```sql
-- DROP TABLE IF EXISTS `tweet-collector-py.impeachment_2021_production.tweets_v2`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_2021_production.tweets_v2` as (
    SELECT
            -- ..
    FROM  `tweet-collector-py.impeachment_2021_production.tweets`
)
```

```sql
-- DROP TABLE IF EXISTS `tweet-collector-py.transition_2021_production.tweets_v2`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.transition_2021_production.tweets_v2` as (
    SELECT
        -- ...
    FROM  `tweet-collector-py.transition_2021_production.tweets`
)
```

## User Details

Aggregating the user-related columns into their own table:


```sql
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.election_2020_production.user_details`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.user_details`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.impeachment_2021_production.user_details`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.transition_2021_production.user_details`;

CREATE TABLE IF NOT EXISTS `tweet-collector-py.election_2020_production.user_details` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.user_details` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_2021_production.user_details` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.transition_2021_production.user_details` as (
    SELECT
        user_id
        --,user_name
        --,user_screen_name
        --,user_description
        --,user_location
        --,user_verified
        --,user_created_at

        ,count(DISTINCT upper(user_screen_name)) as screen_name_count
        ,ARRAY_AGG(DISTINCT upper(user_screen_name) IGNORE NULLS) as screen_names
        ,STRING_AGG(DISTINCT upper(user_screen_name)) as screen_names_csv
        ,ANY_VALUE(upper(user_screen_name)) as screen_name

        ,count(DISTINCT upper(user_name)) as name_count
        ,ARRAY_AGG(DISTINCT upper(user_name) IGNORE NULLS) as names
        ,STRING_AGG(DISTINCT upper(user_name)) as names_csv
        ,ANY_VALUE(user_name) as name

        ,count(DISTINCT upper(user_description)) as description_count
        ,ARRAY_AGG(DISTINCT upper(user_description) IGNORE NULLS) as descriptions
        ,STRING_AGG(DISTINCT upper(user_description)) as descriptions_csv
        ,ANY_VALUE(user_description) as description

        ,count(DISTINCT upper(user_location))	 as location_count
        ,ARRAY_AGG(DISTINCT upper(user_location) IGNORE NULLS) as locations
        --,STRING_AGG(DISTINCT upper(user_location)) as locations_csv
        ,ANY_VALUE(user_location) as location

        ,count(DISTINCT user_verified)	as verified_count --  1
        ,ARRAY_AGG(DISTINCT user_verified IGNORE NULLS) as verifieds
        ,CASE WHEN sum(user_verified) >= 1 THEN true ELSE false END as verified -- if any ones, they will register as true

        ,count(DISTINCT user_created_at) created_at_count
        ,ARRAY_AGG(DISTINCT user_created_at IGNORE NULLS) as created_ats
        ,ANY_VALUE(user_created_at) as created_at


        --


        ,count(DISTINCT status_id) as tweet_count
        ,count(DISTINCT retweeted_status_id) as retweet_count
        ,count(DISTINCT retweeted_user_id) as retweeted_users_count
        ,count(DISTINCT reply_status_id) as reply_count
        ,count(DISTINCT reply_user_id) as reply_users_count
        ,min(created_at) as earliest_tweet_at
        ,max(created_at) as latest_tweet_at



    FROM  `tweet-collector-py.election_2020_production.tweets_v2`
    --FROM  `tweet-collector-py.disinfo_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.impeachment_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.transition_2021_production.tweets_v2`
    GROUP BY user_id

    --LIMIT 10

);
```




## Tweets v2 Slim

Removing user-related columns will make for faster tweet-only queries:

```sql
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.election_2020_production.tweets_v2_slim`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.tweets_v2_slim`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.impeachment_2021_production.tweets_v2_slim`;
-- DROP TABLE IF NOT EXISTS `tweet-collector-py.transition_2021_production.tweets_v2_slim`;

CREATE TABLE IF NOT EXISTS `tweet-collector-py.election_2020_production.tweets_v2_slim` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.tweets_v2_slim` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_2021_production.tweets_v2_slim` as (
--CREATE TABLE IF NOT EXISTS `tweet-collector-py.transition_2021_production.tweets_v2_slim` as (
    SELECT
        status_id
        ,user_id
        ,status_text
        ,truncated
        ,is_quote
        ,geo
        ,created_at

        ,retweeted_status_id
        ,retweeted_user_id

        ,retweeted_user_screen_name --TODO: ,upper(retweeted_user_screen_name) as retweeted_user_screen_name

        ,reply_status_id
        ,reply_user_id

    FROM  `tweet-collector-py.election_2020_production.tweets_v2`
    --FROM  `tweet-collector-py.disinfo_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.impeachment_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.transition_2021_production.tweets_v2`
);
```




## Retweets

## Replies
