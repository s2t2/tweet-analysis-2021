

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

```sql
drop table `tweet-research-shared.disinfo_2021.user_lookups`;
create table `tweet-research-shared.disinfo_2021.user_lookups` (
    user_id INT64,
    error_code INT64,
    follower_count INT64,
    friend_count INT64,
    listed_count INT64,
    status_count INT64,
    latest_status_id INT64,
)
```







# Queries


```sql
-- who are the most active retweeters?
SELECT
    user_id
    ,string_agg(distinct upper(user_screen_name)) as user_screen_names
    ,count(distinct status_id) as rt_count
FROM `tweet-research-shared.disinfo_2021.tweets_view`
WHERE retweeted_status_id is not null
GROUP BY 1
ORDER BY 3 DESC
LIMIT 50
```

```sql
-- who is being retweeting most?
SELECT
    retweeted_user_screen_name
    ,count(distinct user_id) as user_count
    ,count(distinct status_id) as status_count
FROM `tweet-research-shared.disinfo_2021.tweets_view`
WHERE retweeted_user_screen_name is not null
GROUP BY 1
ORDER BY 3 DESC
LIMIT 50
```

## Disinfo Queries

Looks like we have a more generic dataset with mentions of generic terms, so let's restrict the dataset to users who have a higher likelihood of associating with disinfo.


```sql
SELECT
   count(distinct user_id) as user_count
   ,count(distinct status_id) as status_count
FROM `tweet-research-shared.disinfo_2021.tweets_view`
WHERE REGEXP_CONTAINS(upper(status_text), '#WWG1WGA')
```

Get user ids:

```sql
SELECT
    user_id
   ,string_agg(distinct upper(user_screen_name), ", ") as screen_names
   ,any_value(user_verified) as user_verified
   ,any_value(user_created_at) as user_created_at
   ,count(distinct status_id) as status_count

FROM `tweet-research-shared.disinfo_2021.tweets_view`
WHERE REGEXP_CONTAINS(upper(status_text), '#WWG1WGA')
GROUP BY 1
ORDER BY status_count desc
LIMIT 25
```
