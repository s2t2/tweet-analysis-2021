
## Data Warehouse (Shared Environment)

Copying production data to the shared environment...



### Topics

```sql
CREATE TABLE `tweet-research-shared.election_2020.topics` as (
    SELECT * FROM `tweet-collector-py.election_2020_production.topics`
);

CREATE TABLE `tweet-research-shared.disinfo_2021.topics` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.topics`
);

CREATE TABLE `tweet-research-shared.transition_2021.topics` as (
    SELECT * FROM `tweet-collector-py.transition_2021_production.topics`
);

CREATE TABLE `tweet-research-shared.impeachment_2021.topics` as (
    SELECT * FROM `tweet-collector-py.impeachment_2021_production.topics`
);
```

Combined topics across these two similar datasets:

```sql
-- note this will have duplicate topics with different collection start dates if used in different datasets

CREATE TABLE IF NOT EXISTS `tweet-research-shared.election_2020_transition_2021_combined.topics` as (
  SELECT *
  FROM (
    SELECT topic, created_at, 'election_2020' as dataset_name FROM `tweet-research-shared.election_2020.topics` 
    UNION ALL
    SELECT topic, created_at, 'transition_2021' as dataset_name FROM `tweet-research-shared.transition_2021.topics`
  )
  ORDER BY created_at, topic
)

-- de-duping topics
-- SELECT topic, count(dataset_name) as dataset_count, array_agg(dataset_name) as dataset_names, array_agg(created_at) as created_ats
-- FROM `tweet-research-shared.election_2020_transition_2021_combined.topics`
-- GROUP BY 1 
-- ORDER BY 1

 ```
 



### Tweets v2 Slim

```sql
CREATE TABLE `tweet-research-shared.election_2020.tweets_v2_slim` as (
    SELECT * FROM `tweet-collector-py.election_2020_production.tweets_v2_slim`
);

CREATE TABLE `tweet-research-shared.disinfo_2021.tweets_v2_slim` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.tweets_v2_slim`
);

CREATE TABLE `tweet-research-shared.transition_2021.tweets_v2_slim` as (
    SELECT * FROM `tweet-collector-py.transition_2021_production.tweets_v2_slim`
);

CREATE TABLE `tweet-research-shared.impeachment_2021.tweets_v2_slim` as (
    SELECT * FROM `tweet-collector-py.impeachment_2021_production.tweets_v2_slim`
);
```

Combined, tweets across these two similar datasets:

```sql
-- de-duplicate just in case there are overlaps, 
-- although for these two datasets the timelines are different, and we don't have any dups

CREATE TABLE IF NOT EXISTS `tweet-research-shared.election_2020_transition_2021_combined.tweets_v2_slim` as (
  SELECT status_id, user_id, status_text, truncated, is_quote, geo, created_at, 
          retweeted_status_id, retweeted_user_id, retweeted_user_screen_name, reply_status_id, reply_user_id,
          array_agg(distinct dataset_name) as dataset_names
          ,string_agg(distinct dataset_name) as dataset_names_csv
          ,count(distinct dataset_name) as dataset_count
  FROM (
    SELECT status_id, user_id, status_text, truncated, is_quote, geo, created_at, 
          retweeted_status_id, retweeted_user_id, retweeted_user_screen_name, reply_status_id, reply_user_id,
           'election_2020' as dataset_name 
    FROM `tweet-research-shared.election_2020.tweets_v2_slim` -- LIMIT 10

    UNION ALL

    SELECT status_id, user_id, status_text, truncated, is_quote, geo, created_at, 
          retweeted_status_id, retweeted_user_id, retweeted_user_screen_name, reply_status_id, reply_user_id,
           'election_2020' as dataset_name 
    FROM `tweet-research-shared.transition_2021.tweets_v2_slim` -- LIMIT 10
  )
  GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12
  ORDER BY created_at
)
 ```
 
### User Details

```sql
CREATE TABLE `tweet-research-shared.election_2020.user_details` as (
    SELECT * FROM `tweet-collector-py.election_2020_production.user_details`
);

CREATE TABLE `tweet-research-shared.disinfo_2021.user_details` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.user_details`
);

CREATE TABLE `tweet-research-shared.transition_2021.user_details` as (
    SELECT * FROM `tweet-collector-py.transition_2021_production.user_details`
);

CREATE TABLE `tweet-research-shared.impeachment_2021.user_details` as (
    SELECT * FROM `tweet-collector-py.impeachment_2021_production.user_details`
);
```

### Retweets v2

```sql
CREATE TABLE `tweet-research-shared.election_2020.retweets_v2` as (
    SELECT * FROM `tweet-collector-py.election_2020_production.retweets_v2`
);

CREATE TABLE `tweet-research-shared.disinfo_2021.retweets_v2` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.retweets_v2`
);

CREATE TABLE `tweet-research-shared.transition_2021.retweets_v2` as (
    SELECT * FROM `tweet-collector-py.transition_2021_production.retweets_v2`
);

CREATE TABLE `tweet-research-shared.impeachment_2021.retweets_v2` as (
    SELECT * FROM `tweet-collector-py.impeachment_2021_production.retweets_v2`
);
```






### Timeline Tweets

Table ID: tweet-collector-py.disinfo_2021_production.timeline_tweets

Table size: 111.51 GB

Number of rows: 665,378,196

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.timeline_tweets` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets`
);
```

### Friends

Table ID: tweet-collector-py.disinfo_2021_production.friends

Table size: 697.29 MB

Number of rows: 19,594,734

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.friends` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.friends`
);
```

### Followers

Table ID:
 tweet-collector-py.disinfo_2021_production.followers

Table size:
 611.5 MB

Number of rows:
 17,148,293

```sql
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.followers` as (
    SELECT * FROM `tweet-collector-py.disinfo_2021_production.followers`
);
```
