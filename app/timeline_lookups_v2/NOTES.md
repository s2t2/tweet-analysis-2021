
# Queries

```sql
select count(distinct user_id) as user_count
--from `tweet-collector-py.disinfo_2021_production.timeline_tweets` -- 259,034
-- from `tweet-collector-py.disinfo_2021_production.tweets` -- 479,998
-- from `tweet-collector-py.election_2020_production.tweets` -- 2,806,531
-- from `tweet-collector-py.impeachment_2021_production.tweets` -- 1,578,367

```


```sql
```

The joins are taking too long. let's fix this casting up-front:

```sql
drop table if exists `tweet-collector-py.impeachment_production.tweets_slim`;
create table if not exists `tweet-collector-py.impeachment_production.tweets_slim` as (
    SELECT cast(user_id as int64) as user_id, cast(status_id as int64) as status_id
    FROM `tweet-collector-py.impeachment_production.tweets`
)
```

```sql
drop table if exists `tweet-collector-py.disinfo_2021_production.tweets_slim`;
create table if not exists `tweet-collector-py.disinfo_2021_production.tweets_slim` as (
    SELECT cast(user_id as int64) as user_id, cast(status_id as int64) as status_id
    FROM `tweet-collector-py.disinfo_2021_production.tweets`
)
```

```sql
#StandardSQL

WITH all_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.impeachment_production.tweets_slim`
) -- 3,600,545

,collected_disinfo_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
) -- 259,034

SELECT
    count(distinct u.user_id) as user_count
    ,count(distinct case when qu.user_id is not null then u.user_id end) as q_user_count -- 138,072
    ,count(distinct case when qu.user_id is null then u.user_id end) as nonq_user_count -- 3,462,473
FROM all_users u
left join collected_disinfo_users qu ON qu.user_id = u.user_id

```

```sql
#StandardSQL

WITH all_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.impeachment_production.tweets_slim`
) -- 3,600,545

,disinfo_users as (
    SELECT DISTINCT user_id
    FROM `tweet-collector-py.disinfo_2021_production.tweets_slim`
) -- 479,998

,collected_disinfo_users as (
    SELECT distinct user_id
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
) -- 259,034

SELECT
    count(distinct au.user_id) as user_count
FROM all_users au
LEFT JOIN disinfo_users qu ON qu.user_id = au.user_id
LEFT JOIN collected_disinfo_users cqu ON cqu.user_id = au.user_id
WHERE qu.user_id is null AND cqu.user_id is null -- 3,359,798
```

There are 3.3M eligible users. Let's sample them by their characteristics. Is it possible to stratify in BigQuery?
