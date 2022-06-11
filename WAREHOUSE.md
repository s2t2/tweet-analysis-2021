
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
