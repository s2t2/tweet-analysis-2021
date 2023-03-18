
# Data Prep and Cleaning

For reporting on what has been collected, and preparing the dataset for further analysis.

## Collection Totals



Original stream listeners collected 37.3M unique tweets:

```sql
SELECT
  count(distinct status_id) as status_count
FROM (
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.disinfo_2021_production.tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.election_2020_production.tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.transition_2021_production.tweets`
    UNION ALL
    SELECT distinct cast(status_id as int64) as status_id FROM `tweet-collector-py.impeachment_2021_production.tweets`
) -- 37,352,881
```

Including timeline tweet re-collection, there are 698 million unique tweets total:

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




<hr>

# Migrations

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




## User Profile Tags

Repeat these queres for all datasets:

  + `tweet-research-shared.election_2020`
  + `tweet-research-shared.disinfo_2021` (TODO)
  + `tweet-research-shared.impeachment_2021`
  + `tweet-research-shared.transition_2021`


```sql
DROP TABLE IF EXISTS `tweet-research-shared.election_2020.profile_tags`;
CREATE TABLE `tweet-research-shared.election_2020.profile_tags` as (
  SELECT
    user_id
    ,REGEXP_EXTRACT_ALL(upper(p.descriptions_csv), r'#[A-Z0-9]+') as tags
  FROM `tweet-research-shared.election_2020.user_details` p
  WHERE REGEXP_CONTAINS(p.descriptions_csv, '#')
  -- LIMIT 10
)

--WITH tag_counts as (
--  SELECT user_id, array_length(tags) as tags_count
--  FROM `tweet-research-shared.election_2020.profile_tags`
--)
--SELECT * FROM tag_counts WHERE tags_count > 1
```

```sql
-- this is a distinct table of user profile tags
CREATE TABLE `tweet-research-shared.election_2020.profile_tags_flat` as (
    SELECT DISTINCT user_id, tag
    FROM (
        SELECT user_id, tag
        FROM `tweet-research-shared.election_2020.profile_tags`
        CROSS JOIN UNNEST(tags) AS tag
        --LIMIT 1000
    )
)
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

### Retweets v2

Repeat this query for the following datasets (change in all three places):
  + `tweet-collector-py.election_2020_production`
  + `tweet-collector-py.disinfo_2021_production`
  + `tweet-collector-py.impeachment_2021_production`
  + `tweet-collector-py.transition_2021_production`

```sql
CREATE TABLE IF NOT EXISTS `tweet-collector-py._____.retweets_v2` as (
    -- screen names included for convenience, but prefer to use ids for analysis purposes
    SELECT
        t.user_id
        ,u.screen_name as user_screen_name
        -- u.created_at as user_created_at

        ,t.retweeted_user_id
        ,UPPER(t.retweeted_user_screen_name) as retweeted_user_screen_name

        ,t.status_id
        ,t.status_text
        ,t.created_at

    FROM `tweet-collector-py.______.tweets_v2_slim` t
    LEFT JOIN `tweet-collector-py.______.user_details` u ON t.user_id = u.user_id
    WHERE t.retweeted_status_id IS NOT NULL
        AND t.user_id <> t.retweeted_user_id
        -- and u.screen_name is null -- there are no nulls when doing a left join. so could do inner join instead
    -- LIMIT 10
);
```
