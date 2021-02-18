

# Database Queries and Migrations

## Stream Listener

Monitoring results:

```sql
SELECT
    extract(date from created_at) as day
    ,count(distinct user_id) as user_count
    ,count(distinct status_id) as status_count
    ,count(distinct case when retweeted_status_id is not null then status_id end) as rt_count
FROM `tweet-collector-py.disinfo_2021_production.tweets`
-- FROM `tweet-collector-py.impeachment_2021_production.tweets`
-- FROM `tweet-collector-py.transition_2021_production.tweets`
-- FROM `tweet-collector-py.election_2020_production.tweets`
-- FROM `tweet-collector-py.impeachment_production.tweets`
GROUP BY 1
ORDER BY 1 DESC
```

## User Lookups

User lookups script:

```sql
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

> NOTE: We originally created this table in the shared analysis environment, but it is better to collect data into the upstream data environment. So here is a one-time query that was used retrospectively to backup the data into the upstream environment:
>
>```sql
> -- DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.user_lookups`;
> -- CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.user_lookups` as (
> --     SELECT DISTINCT user_id, error_code, follower_count, friend_count, listed_count, status_count, latest_status_id
> --     FROM `tweet-research-shared.disinfo_2021.user_lookups`
> -- )
>```

Monitoring the results:

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

## Timeline Lookups

Timeline lookups script:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.timeline_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.timeline_lookups` (
    user_id INT64,
    timeline_length INT64,
    error_type STRING,
    error_message STRING,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
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

    lookup_at TIMESTAMP
)
```

Monitoring the results:

```sql
SELECT
  error_message
  ,count(distinct user_id) as user_count
  ,sum(timeline_length) as tweet_count
  ,avg(timeline_length) as tweet_avg
FROM `tweet-collector-py.disinfo_2021_production.timeline_lookups`
GROUP BY 1
--ORDER BY  start_at desc
--LIMIT 10
```

```sql
-- see: https://developer.twitter.com/ja/docs/basics/response-codes
SELECT
    error_type
    ,error_code
    ,case when error_message like "%401%" THEN "Unauthorized"
        when error_message like "%500%" THEN "Internal Server Error"
        when error_message like "%503%" THEN "Service Unavailable"
        else error_message
    end error_message
   ,count(distinct user_id) as user_count
   ,sum(timeline_length) as tweet_count
FROM `tweet-collector-py.disinfo_2021_production.timeline_lookups`
group by 1,2,3
order by user_count desc
```

```sql
SELECT
  count(distinct user_id) as user_count
  ,count(distinct status_id) as status_count
FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
```

```sql
SELECT
  extract(date from lookup_at) as lookup_on
  ,count(distinct user_id) as user_count
  ,count(distinct status_id) as status_count
FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
GROUP BY 1
ORDER BY 1 DESC
```

Distribution of timeline tweets over time (by day):

```sql
SELECT
  extract(date from created_at) as created_on
  ,count(distinct user_id) as user_count
  ,count(distinct status_id) as status_count
FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
GROUP BY 1
ORDER BY 1 DESC
```

<hr>

## Downstream Views (Analysis Environment)

Copying some of the production data to the shared environment, to test our ability to query it from our Colab notebooks (where we are using a more limited set of credentials):

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
