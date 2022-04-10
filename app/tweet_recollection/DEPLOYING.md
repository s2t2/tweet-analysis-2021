
## Deploying

Run this on server 6.

Configuring:

```sh
heroku config:set TWITTER_API_KEY="_________" -r heroku-6
heroku config:set TWITTER_API_KEY_SECRET="_______" -r heroku-6
heroku config:set TWITTER_ACCESS_TOKEN="________" -r heroku-6
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="____________" -r heroku-6
heroku config:set TWITTER_ENVIRONMENT_NAME="______" -r heroku-6
```

Deploying:

```sh
git push heroku-6 recollection:main -f
```

Turn on the "tweet_recollector" dyno.

Monitoring:

```sh
heroku logs --tail -r heroku-6
```

## Results

Recollected 36M of 65M tweets (56%)

```sql
SELECT
   count(distinct status_id) as status_count
   ,count(distinct case when full_text is not null then status_id end) as success_count
   ,count(distinct case when full_text is not null then status_id end) / count(distinct status_id) as success_pct
FROM `tweet-collector-py.impeachment_production.recollected_statuses`

-- SELECT * FROM `tweet-collector-py.impeachment_development.recollected_statuses` LIMIT 100
-- SELECT * FROM `tweet-collector-py.impeachment_development.recollected_status_urls`  LIMIT 100
```

status_count	| success_count	| success_pct
--- | --- | ---
65,382,222	| 36,637,003	| 0.5603511456065228

Of those 36M tweets, we collected 7.5M urls (1.3 distinct urls).

```sql
SELECT
  count( status_id) as urls_count
  ,count(distinct expanded_url)  as distinct_urls_count
FROM `tweet-collector-py.impeachment_production.recollected_status_urls`
```


urls_count	| distinct_urls_count
--- | ---
7,513,868	| 1,380,415
