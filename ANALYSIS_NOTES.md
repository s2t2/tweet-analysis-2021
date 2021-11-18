# Analysis Notes

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
) -- 687,833,005
```

From a variety of collection efforts:

```sql
SELECT 
  count(distinct status_id) as status_count
  ,count(distinct user_id) as user_count
--FROM `tweet-collector-py.disinfo_2021_production.tweets` -- 1,521,270 | 479,998
-- FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` -- 664,990,206 | 259,034
-- FROM `tweet-collector-py.election_2020_production.tweets` -- 17,047,192 | 2,806,531
FROM `tweet-collector-py.transition_2021_production.tweets` -- 5,263,947 | 1,012,626
```

dataset | tweets | users
--- | --- | ---
`tweet-collector-py.disinfo_2021_production.tweets` | 1,521,270 | 479,998
`tweet-collector-py.disinfo_2021_production.timeline_tweets`| 664,990,206 | 259,034
`tweet-collector-py.election_2020_production.tweets` | 17,047,192 | 2,806,531
`tweet-collector-py.transition_2021_production.tweets` | 5,263,947 | 1,012,626
