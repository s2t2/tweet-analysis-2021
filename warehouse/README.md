
# Managing the Shared Data Environment

First, make the [upstream data](UPSTREAM.md), as necessary, in source datasets.

Then copy production data to the shared environment, where it can be accessible to other researchers...

## Dataset-specific Tables

These tables are found within a given dataset.

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








<hr>















## Cross-Dataset Tables

These tables represent a mixture of data from all datasets. This helps for faster lookups and broadens the set of possible analyses.

These tables should be re-migrated after new datasets are added, to include additional columns for the new dataset.

### All Tweets

One table of tweet ids to rule them all.

```sql
--CREATE TABLE `tweet-research-shared.warehouse.all_tweet_ids` as (
--
--);



```
