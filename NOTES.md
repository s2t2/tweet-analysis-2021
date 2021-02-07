

# Migrations

```sql
create table `tweet-research-shared.disinfo_2021.topics_view` as (
    select *
    from `tweet-collector-py.disinfo_2021_production.topics`
)
```

```sql
drop table `tweet-research-shared.disinfo_2021.tweets_view`;
create table `tweet-research-shared.disinfo_2021.tweets_view` as (
    select
        cast(status_id as int64) as status_id
        ,status_text
        ,truncated
        ,cast(retweeted_status_id as int64) as retweeted_status_id
        ,retweeted_user_screen_name
        ,cast(reply_status_id as int64) as reply_status_id
        ,cast(reply_user_id as int64) as reply_user_id
        ,is_quote
        ,geo
        ,created_at

        ,cast(user_id as int64) as user_id
        ,user_name
        ,user_screen_name
        ,user_description
        ,user_location
        ,user_verified
        ,user_created_at
    from `tweet-collector-py.disinfo_2021_production.tweets`
    --LIMIT 10
)
```

### User Lookups

User lookups script:

```sql
--drop table `tweet-research-shared.disinfo_2021.user_lookups`;
--create table `tweet-research-shared.disinfo_2021.user_lookups` (
-- NEXT TIME DO THIS INSTEAD:
drop table `tweet-collector-py.disinfo_2021_production.user_lookups`;
create table `tweet-collector-py.disinfo_2021_production.user_lookups` (
    user_id INT64,
    error_code INT64,
    follower_count INT64,
    friend_count INT64,
    listed_count INT64,
    status_count INT64,
    latest_status_id INT64,
)
```

We should actually probably be collecting in the upstream project only, so let's at least backup there retrospectively:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.user_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.user_lookups` as (
    SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
    FROM `tweet-research-shared.disinfo_2021.user_lookups`
)
```


### Timeline Lookups

Timeline lookups script:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.timeline_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.timeline_lookups` (
    user_id INT64,
    timeline_length INT64,
    -- start_at TIMESTAMP, -- todo add this column next time
    -- end_at TIMESTAMP, -- todo add this column next time
    error_code INT64,
    error_type STRING,
    error_message STRING
);
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.timeline_tweets`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.timeline_tweets` (
    user_id INT64,
    status_id INT64,
    status_text STRING,
    created_at TIMESTAMP,

    geo STRING,
    is_quote BOOLEAN,
    truncated BOOLEAN,

    reply_status_id INT64,
    reply_user_id INT64,
    retweeted_status_id INT64,
    retweeted_user_id INT64,
    retweeted_user_screen_name STRING,
)
```




# Queries

Tweet Collection Progress:

```sql
SELECT
    extract(date from created_at) as day
    ,count(distinct user_id) as user_count
    ,count(distinct status_id) as status_count
    ,count(distinct case when retweeted_status_id is not null then status_id end) as rt_count
FROM `tweet-research-shared.disinfo_2021.tweets_view`
-- FROM `tweet-collector-py.disinfo_2021_production.tweets`
-- FROM `tweet-collector-py.impeachment_2021_production.tweets`
GROUP BY 1
ORDER BY 1 DESC
```

User Lookup Results:

```sql
-- see: https://developer.twitter.com/ja/docs/basics/response-codes
SELECT
    error_code
    ,case
        when error_code = 50 then "User not found."
        when error_code = 63 then "User has been suspended."
    end  error_message
   ,count(distinct user_id) as user_count
   ,sum(status_count) as tweet_count
FROM `tweet-research-shared.disinfo_2021.user_lookups`
group by 1,2
order by 3 desc
```

Timeline Lookup Results:

```sql
-- see: https://developer.twitter.com/ja/docs/basics/response-codes
SELECT
    error_type
    ,error_code
    ,case when error_message like "%401%" THEN "Unauthorized"
        when error_message like "%503%" THEN "Service Unavailable"
        else error_message
    end error_message
   ,count(distinct user_id) as user_count
   ,sum(timeline_length) as tweet_count
FROM `tweet-collector-py.disinfo_2021_production.timeline_lookups`
group by 1,2,3
order by user_count desc
```
