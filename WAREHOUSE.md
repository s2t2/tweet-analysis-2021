
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
