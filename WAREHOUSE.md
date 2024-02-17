
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





#### Q User Timelines

Filter timeline tweets to include only those users identified as q from our previous paper. Prepare a dataset of these user's timeline tweets.

```sql
-- SELECT count(distinct user_id) as q_count -- 25_360
-- FROM `tweet-collector-py.impeachment_production.user_details_v20240128_slim` u
-- WHERE is_q = true

-- q users from previous dataset
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.q_user_details_v2020` as (
    SELECT  
        user_id, created_on
        ,screen_name_count, screen_names
        , status_count, rt_count , q_status_count ,is_q
        ,is_bot, opinion_community
        
        ,avg_toxicity, avg_severe_toxicity, avg_insult, avg_obscene, avg_threat , avg_identity_hate
        ,fact_scored_count ,avg_fact_score
    FROM `tweet-collector-py.impeachment_production.user_details_v20240128_slim` u
    WHERE is_q = true
    ORDER BY q_status_count DESC
    -- LIMIT 10
)


-- summary table for timelines from these users (all tweets vs original only)

SELECT count(distinct t.user_id) as user_count -- 4,718
  ,count(distinct case when u.is_bot = true then u.user_id end) as bot_count -- 553
  , count(distinct t.status_id) as status_count -- 11,982,573 WOW
  ,date(min(created_at)) as first_created -- 2008-09-22
  ,date(max(created_at)) as last_created -- 2021-05-15
  ,date(min(lookup_at)) as first_lookup -- 2021-02-10
  ,date(max(lookup_at)) as last_lookup -- 2021-05-15
  ,count(distinct case when geo is not null and geo <> "" then status_id end) geo_count -- 7,530,129
  ,count(distinct case when truncated = true then status_id end) truncated_count -- 0
  ,count(distinct case when is_quote = true then status_id end) quote_count -- 2,201,073
  ,count(distinct case when reply_status_id is not null then status_id end) reply_count -- 2,353,637
  ,count(distinct reply_status_id) as reply_status_count -- 1,715,274
  ,count(distinct case when retweeted_status_id is not null then status_id end) rt_count -- 7,750,753
  ,count(distinct retweeted_status_id) as rt_status_count -- 3,197,332
  ,count(distinct retweeted_user_id) as rt_user_count -- 386,285

FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` t
JOIN `tweet-research-shared.disinfo_2021.q_user_details_v2020` u on t.user_id = u.user_id
-- WHERE t.is_quote <> true and t.reply_status_id is null and t.retweeted_status_id is null


-- summary of timeline tweets for q users from previous dataset
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.q_user_timeline_details` as (
    SELECT u.user_id -- 4,718
      --,u.is_bot, u.avg_fact_score, u.avg_toxicity
      , count(distinct t.status_id) as status_count 
      ,count(distinct case when is_quote = true then status_id end) quote_count 
      ,count(distinct case when reply_status_id is not null then status_id end) reply_count
      ,count(distinct case when retweeted_status_id is not null then status_id end) rt_count 
      ,count(distinct case when (t.is_quote <> true and t.reply_status_id is null and t.retweeted_status_id is null) then status_id end) original_count

      ,date(min(created_at)) as created_earliest
      ,date(max(created_at)) as created_latest 
      ,date(min(lookup_at)) as lookup_earliest 
      ,date(max(lookup_at)) as lookup_latest 

      ,count(distinct case when geo is not null and geo <> "" then status_id end) geo_count 
      --,count(distinct case when truncated = true then status_id end) truncated_count 

      ,count(distinct reply_status_id) as reply_status_count -- 1,715,274
      ,count(distinct retweeted_status_id) as rt_status_count -- 3,197,332
      ,count(distinct retweeted_user_id) as rt_user_count -- 386,285

    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` t
    JOIN `tweet-research-shared.disinfo_2021.q_user_details_v2020` u on t.user_id = u.user_id
    -- WHERE t.is_quote <> true and t.reply_status_id is null and t.retweeted_status_id is null
    GROUP BY 1
    ORDER BY status_count DESC
    -- LIMIT 10
)

-- timeline tweets for q users from previous dataset
CREATE TABLE IF NOT EXISTS `tweet-research-shared.disinfo_2021.q_user_timeline_tweets_original` as (
    SELECT 
      t.user_id, t.status_id, t.status_text, t.geo, t.created_at, t.lookup_at
         --, t.truncated
        --,t.is_quote
        --,t.reply_status_id , t.reply_user_id
        --,t.retweeted_status_id, t.retweeted_user_id, t.retweeted_user_screen_name
    FROM `tweet-collector-py.disinfo_2021_production.timeline_tweets` t
    JOIN `tweet-research-shared.disinfo_2021.q_user_details_v2020` u on t.user_id = u.user_id
    WHERE t.is_quote <> true and t.reply_status_id is null and t.retweeted_status_id is null
    ORDER BY user_id, created_at
    -- LIMIT 10
)



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
