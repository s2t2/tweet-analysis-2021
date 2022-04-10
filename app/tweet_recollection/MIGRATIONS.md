
# Queries and Migrations

Make a dataset called "analysis_2021" as necessary. And one called "analysis_2021_development" as well.

## All Status Ids

Let's union all the tweets to be looked up.

> NOTE: including the "impeachment_2020" tweets in this table. But when recollecting, make sure to filter these out because we have already [recollected them](https://github.com/s2t2/tweet-analysis-2020/tree/main/app/tweet_recollection).


```sql
CREATE TABLE IF NOT EXISTS `tweet-collector-py.analysis_2021.all_status_ids` as (
    SELECT
        status_id
        ,sum(impeachment_2020) as impeachment_2020
        ,sum(election_2020) as election_2020
        ,sum(transition_2021) as transition_2021
        ,sum(impeachment_2021) as impeachment_2021
        ,sum(disinfo_2021) as disinfo_2021
        ,sum(disinfo_timeline) as disinfo_timeline
    FROM (

        SELECT
            distinct cast(status_id as int64) as status_id
            ,1 as impeachment_2020 --
            ,0 as election_2020
            ,0 as transition_2021
            ,0 as impeachment_2021
            ,0 as disinfo_2021
            ,0 as disinfo_timeline
        FROM `tweet-collector-py.impeachment_production.tweets`

        UNION ALL

        SELECT
            distinct cast(status_id as int64) as status_id
            ,0 as impeachment_2020
            ,1 as election_2020 --
            ,0 as transition_2021
            ,0 as impeachment_2021
            ,0 as disinfo_2021
            ,0 as disinfo_timeline
        FROM `tweet-collector-py.election_2020_production.tweets`

        UNION ALL

        SELECT
            distinct cast(status_id as int64) as status_id
            ,0 as impeachment_2020
            ,0 as election_2020
            ,1 as transition_2021 --
            ,0 as impeachment_2021
            ,0 as disinfo_2021
            ,0 as disinfo_timeline
        FROM `tweet-collector-py.transition_2021_production.tweets`

        UNION ALL

        SELECT
            distinct cast(status_id as int64) as status_id
            ,0 as impeachment_2020
            ,0 as election_2020
            ,0 as transition_2021
            ,1 as impeachment_2021 --
            ,0 as disinfo_2021
            ,0 as disinfo_timeline
        FROM `tweet-collector-py.impeachment_2021_production.tweets`

        UNION ALL

        SELECT
            distinct cast(status_id as int64) as status_id
            ,0 as impeachment_2020
            ,0 as election_2020
            ,0 as transition_2021
            ,0 as impeachment_2021
            ,1 as disinfo_2021 --
            ,0 as disinfo_timeline
        FROM `tweet-collector-py.disinfo_2021_production.tweets`

        UNION ALL

        SELECT
            distinct cast(status_id as int64) as status_id
            ,0 as impeachment_2020
            ,0 as election_2020
            ,0 as transition_2021
            ,0 as impeachment_2021
            ,0 as disinfo_2021
            ,1 as disinfo_timeline --
        FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`

    )
    GROUP BY 1
    --LIMIT 10
);

```

Ensure there are no duplicate records:

```sql
SELECT status_id, count(*) as row_count
FROM `tweet-collector-py.analysis_2021.all_status_ids`
GROUP BY 1
HAVING row_count > 1
```

Observe the total overlap counts:

```sql

WITH status_ids AS (
    SELECT
        *

        ,(impeachment_2020 + election_2020 + transition_2021
            + impeachment_2021 + disinfo_2021 + disinfo_timeline) as dataset_count
    FROM `tweet-collector-py.analysis_2021.all_status_ids`
)

SELECT count(distinct status_id)
FROM status_ids -- 765,966,689

-- TWEETS APPEARING ACROSS MULTIPLE DATASETS...
--WHERE dataset_count > 1                          -- 4,107,899
--WHERE dataset_count > 1 and impeachment_2020=1    --  198,955
--WHERE dataset_count > 1 and election_2020=1       --  231,866
--WHERE dataset_count > 1 and transition_2021=1    --   410,310
--WHERE dataset_count > 1 and impeachment_2021=1   -- 2,940,764
--WHERE dataset_count > 1 and disinfo_2021=1       --   412,378
--WHERE dataset_count > 1 and disinfo_timeline=1   -- 4,042,955

-- TWEETS APPEARING IN ONE DATASET...
-- WHERE dataset_count =1                           -- 761,858,790
--WHERE dataset_count = 1 and impeachment_2020=1    --  67,467,602
--WHERE dataset_count = 1 and election_2020=1       --  16,815,326
--WHERE dataset_count = 1 and transition_2021=1     --   4,853,637
--WHERE dataset_count = 1 and impeachment_2021=1    --  10,666,082
--WHERE dataset_count = 1 and disinfo_2021=1        --   1,108,892
--WHERE dataset_count = 1 and disinfo_timeline=1    -- 660,947,251

```


Copy to development (so we can test things out first):

```sql
CREATE TABLE IF NOT EXISTS `tweet-collector-py.analysis_2021_development.all_status_ids` as (
    SELECT *
    FROM `tweet-collector-py.analysis_2021.all_status_ids`
);
```


## Recollected Statuses and URLs


Now making tables to store the new status and url lookups:

```sql
--DROP TABLE IF EXISTS `tweet-collector-py.analysis_2021.recollected_statuses`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.analysis_2021.recollected_statuses` (
    status_id INT64,
    user_id INT64,
    full_text STRING,
    created_at TIMESTAMP,
    lookup_at TIMESTAMP
);

--DROP TABLE IF EXISTS `tweet-collector-py.analysis_2021.recollected_status_urls`;
CREATE TABLE IF NOT EXISTS `tweet-collector-py.analysis_2021.recollected_status_urls` (
    status_id INT64,
    expanded_url STRING,
    --unwound_url STRING,
    --unwound_title STRING,
    --unwound_description STRING,
);
```

Make these tables on development as well.


<hr>


# Monitoring

Monitoring results:

```sql
SELECT
   count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
FROM `tweet-collector-py.analysis_2021.recollected_statuses`
```

```sql
SELECT
   count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
FROM `tweet-collector-py.analysis_2021.recollected_statuses`
```
