
# Data Warehouse Notes

For reporting on what has been collected, and preparing the dataset for further analysis.


## Collection Totals


We have collected 687 million unique tweets total.

```sql
SELECT
  count(distinct status_id) as status_count
FROM (
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.disinfo_2021_production.tweets`
    UNION ALL
    SELECT distinct status_id FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.election_2020_production.tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.transition_2021_production.tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.impeachment_2021_production.tweets`
) -- 698,499,087
```

From a variety of collection efforts:

```sql
SELECT
  count(distinct status_id) as status_count
  ,count(distinct user_id) as user_count
--FROM `tweet-collector-py.disinfo_2021_production.tweets` -- 1,521,270 | 479,998
-- FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` -- 664,990,206 | 259,034
-- FROM `tweet-collector-py.election_2020_production.tweets` -- 17,047,192 | 2,806,531
-- FROM `tweet-collector-py.transition_2021_production.tweets` -- 5,263,947 | 1,012,626
FROM `tweet-collector-py.impeachment_2021_production.tweets` -- 13606846 | 1578367

```

dataset | tweets | users
--- | --- | ---
`tweet-collector-py.disinfo_2021_production.tweets` | 1,521,270 | 479,998
`tweet-collector-py.disinfo_2021_production.timeline_tweets`| 664,990,206 | 259,034
`tweet-collector-py.election_2020_production.tweets` | 17,047,192 | 2,806,531
`tweet-collector-py.transition_2021_production.tweets` | 5,263,947 | 1,012,626
`tweet-collector-py.impeachment_2021_production.tweets` | 13,606,846 | 1,578,367


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

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.impeachment_2020.retweets_v2` as (
    SELECT *
        FROM `tweet-collector-py.impeachment_production.retweets_v2`
        -- LIMIT 10
)
```
