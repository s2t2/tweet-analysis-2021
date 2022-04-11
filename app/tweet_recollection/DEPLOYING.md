
## Deploying

Run this on server "tweet-analysis-2021" (remote name "heroku").

Configuring:

```sh
# use the production dataset:
heroku config:set ANALYSIS_DATASET_ADDRESS="analysis_2021" -a tweet-analysis-2021
```

Deploying:

```sh
git push heroku recollect:main -f
```

Turn on the "tweet_recollector" dyno.

Monitoring:

```sh
heroku logs --tail -a tweet-analysis-2021
```

## Results and Monitoring

Recollected X of 35.5M tweets (Y%):

```sql
SELECT
   count(*) as row_count
   ,count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
--FROM `tweet-collector-py.analysis_2021_development.recollected_statuses`
FROM `tweet-collector-py.analysis_2021.recollected_statuses`
```

status_count	| success_count	| success_pct
--- | --- | ---
...	| ... | ...

Of those X tweets, we collected U urls (Z distinct urls).

```sql
SELECT
  count( status_id) as urls_count
  ,count(distinct expanded_url)  as distinct_urls_count
--FROM `tweet-collector-py.analysis_2021_development.recollected_status_urls`
FROM `tweet-collector-py.analysis_2021.recollected_status_urls`
```


urls_count	| distinct_urls_count
--- | ---
...	| ...
