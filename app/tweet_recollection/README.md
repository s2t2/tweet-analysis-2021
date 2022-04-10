## Tweet Re-Collection

Requirements (two birds one stone):

  1. We have retweets of the original tweet, but in some cases not the original tweet itself, so let's lookup the original tweets (retweets, and replies while we're at it).
  2. Some of the texts are truncated. It would be nice to have non-truncated / full texts (really this time).
  3. We need the full, non-truncated url(s) shared in the tweet text (so we can do news credibility analysis on the domains).

Limitations:
  + Some user accounts have been deactivated.
  + Some of the original tweets have since been deleted.

Strategy:
  + We're going to do a second pass over tall the tweet ids we have in the dataset, including retweet targets, and lookup their full text and urls.

## [Migrations](MIGRATIONS.md)

First run migrations to assemble a list of tweet ids to recollect.

## Usage

Running the job locally:

```sh
ANALYSIS_DATASET_ADDRESS="tweet-collector-py.analysis_2021_development" STATUS_LIMIT=100 BATCH_SIZE=10 python -m app.tweet_recollection.collector
```

## [Deploying](DEPLOYING.md)

Run the job on the server.
