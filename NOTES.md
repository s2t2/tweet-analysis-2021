

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


## Friend Lookups

Friend lookups script:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.friend_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.friend_lookups` (
    user_id INT64,
    friend_count INT64,
    error_type STRING,
    error_message STRING,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
);
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.friends`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.friends` (
    user_id INT64,
    --screen_name STRING,

    friend_id INT64,
    friend_name STRING,

    lookup_at TIMESTAMP
)
```

Monitoring the results:

```sql
SELECT
  count(distinct user_id) as user_count
  ,sum(friend_count) as friend_count
  ,avg(friend_count) as friend_avg
  ,max(friend_count) as friend_max
FROM `tweet-collector-py.disinfo_2021_production.friend_lookups`

```

```sql
SELECT
  count(distinct user_id) as user_count
  ,count(distinct concat(user_id, "--", friend_id)) as friendship_count
FROM `tweet-collector-py.disinfo_2021_production.friends`
```

```sql
SELECT
  extract(date from lookup_at) as lookup_on
  ,count(distinct user_id) as user_count
  ,count(distinct concat(user_id, "--", friend_id)) as friendship_count
FROM `tweet-collector-py.disinfo_2021_production.friends`
GROUP BY 1
ORDER BY 1 DESC
```

## Follower Lookups

Follower lookups script:

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.follower_lookups`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.follower_lookups` (
    user_id INT64,
    follower_count INT64,
    error_type STRING,
    error_message STRING,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
);
```

```sql
DROP TABLE IF EXISTS `tweet-collector-py.disinfo_2021_production.followers`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.disinfo_2021_production.followers` (
    user_id INT64,
    --screen_name STRING,

    follower_id INT64,
    follower_name STRING,

    lookup_at TIMESTAMP
)
```

Monitoring the results:


```sql
SELECT
  count(distinct user_id) as user_count
  ,sum(follower_count) as follower_count
  ,avg(follower_count) as follower_avg
  ,max(follower_count) as follower_max
FROM `tweet-collector-py.disinfo_2021_production.follower_lookups`
```

```sql
SELECT
  count(distinct user_id) as user_count
  ,count(distinct concat(user_id, "--", follower_id)) as followship_count
FROM `tweet-collector-py.disinfo_2021_production.followers`
```

```sql
SELECT
  extract(date from lookup_at) as lookup_on
  ,count(distinct user_id) as user_count
  ,count(distinct concat(user_id, "--", follower_id)) as followship_count
FROM `tweet-collector-py.disinfo_2021_production.followers`
GROUP BY 1
ORDER BY 1 DESC
```

## Continuous Tweet Collection

Users with successful timeline lookups:

```sql
SELECT
  user_id
  ,count(distinct status_id) as status_count
  ,max(status_id) as latest_status
  --,extract(date from min(created_at)) as earliest_on
  --,extract(date from max(created_at)) as latest_on
  ,extract(date from max(lookup_at)) as latest_lookup
FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
GROUP BY 1
ORDER BY 4
```




## Complete Networks

Friend and follower collection moves slower, so we only have a F/F network for a fraction of the total users. For how many users have we collected everything (i.e. tweets, friends, and followers)? We can use these "completed" users for our analysis:

```sql
--SELECT
--   count(distinct t.user_id) as user_count
--   ,count(distinct t.status_id) as status_id
--   ,count(distinct friends.friend_id) as friend_count
--    ,count(distinct followers.follower_id) as follower_count
--FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` t
--LEFT JOIN `tweet-collector-py.disinfo_2021_production.friends` friends ON t.--user_id = friends.user_id
--LEFT JOIN `tweet-collector-py.disinfo_2021_production.followers` followers ON t.--user_id = followers.user_id
--WHERE t.user_id IS NOT NULL
--    AND friends.user_id IS NOT NULL
--    AND followers.user_id IS NOT NULL
--


SELECT
   count(distinct disinfo_users.user_id) as user_count
   ,sum(disinfo_users.status_count ) as status_count
   ,sum(friends.friend_count) as friend_count
   ,sum(followers.follower_count) as follower_count
FROM (
    SELECT user_id ,count(distinct status_id) as status_count
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
    GROUP BY 1
) disinfo_users
JOIN (
    SELECT user_id ,count(distinct friend_id) as friend_count
    FROM `tweet-collector-py.disinfo_2021_production.friends`
    GROUP BY 1
) friends ON disinfo_users.user_id = friends.user_id
JOIN (
    SELECT user_id ,count(distinct follower_id) as follower_count
    FROM `tweet-collector-py.disinfo_2021_production.followers`
    GROUP BY 1
) followers ON disinfo_users.user_id = followers.user_id


```
