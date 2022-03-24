
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

## Tweets v2 Slim

Removing user-related columns will make for faster tweet-only queries:

```sql
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
        ,retweeted_user_screen_name

        ,reply_status_id
        ,reply_user_id

    FROM  `tweet-collector-py.election_2020_production.tweets_v2`
    --FROM  `tweet-collector-py.disinfo_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.impeachment_2021_production.tweets_v2`
    --FROM  `tweet-collector-py.transition_2021_production.tweets_v2`
);
```


## User Details

Aggregating the user-related columns into their own table:

```sql

```

## Retweets

## Replies
