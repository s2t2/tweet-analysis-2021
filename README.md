# tweet-analysis-2021

This repo provides a fresh start follow-up to our [previous research code](https://github.com/s2t2/tweet-analyzer-py), in which we collected and analyzed tweets about the First Trump Impeachment. This repo supports the collection and analysis of tweets for subsequent events of interest: including the 2020 Election, 2021 Presidential Transition, the Second Trump Impeachment, as well as a generic longitudinal collection of disinformation-related tweets.

If you are a researcher interested in accessing our data, or using this codebase to collect your own tweets of interest, feel free to reach out.

## Installation

Clone this repo onto your local machine and navigate there from the command-line:

```sh
cd path/to/tweet-analysis-2021/
```

Create and activate a virtual environment, using anaconda for example, if you like that kind of thing:

```sh
conda create -n tweets-env-2021 python=3.8
conda activate tweets-env-2021
```

Install package dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

### Twitter API Credentials

From the [Twitter Developer console](https://developer.twitter.com), create a new app and corresponding credentials which provide read access to the Twitter API. Set the environment variables `TWITTER_API_KEY`, `TWITTER_API_KEY_SECRET`, `TWITTER_ACCESS_TOKEN`, and `TWITTER_ACCESS_TOKEN_SECRET` accordingly (see environment variable setup below).

### Google API Credentials

From the [Google Cloud console](https://console.cloud.google.com/), enable the BigQuery API, then generate and download the corresponding service account credentials. Move them into the root directory of this repo as "google-credentials.json", and set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable accordingly (see environment variable setup below).

> NOTE: to access the "tweet-research-shared" BigQuery data environment, you can download the credentials file from the shared drive (see "credentials" directory)! 

### Environment Variables

Create a new file in the root directory of this repo called ".env", and set your environment variables there, as necessary:

```sh
# example .env file

GOOGLE_APPLICATION_CREDENTIALS="/path/to/tweet-analysis-2021/google-credentials.json"
#DATASET_ADDRESS="tweet-collector-py.disinfo_2021_development"

TWITTER_API_KEY="_____________"
TWITTER_API_KEY_SECRET="_____________"
TWITTER_ACCESS_TOKEN="_____________"
TWITTER_ACCESS_TOKEN_SECRET="_____________"
```

## Usage

### Services

Connecting with Google BigQuery database:

```sh
python -m app.bq_service
```

Connecting with the Twitter API:

```sh
python -m app.twitter_service
```

### Jobs / Worker Processes

We start by collecting tweets in real-time using a Stream Listener approach. Then we follow-up with a historic collection of tweets for selected users, using the Search API.

#### Twitter Stream Listener

Use the ["tweet_collection_v2" code](https://github.com/s2t2/tweet-analyzer-py/tree/master/app/tweet_collection_v2) from the previous repo to collect tweets mentioning one of a number of specified terms.

> NOTE: there is a plan to copy the stream listener code and integrate it into this repository in the near future.

#### Twitter Search API

Lookup user information, for users in our dataset who tweeted using a specified search term, optionally specifying a max number of users to fetch:

```sh
SEARCH_TERM="#MySearchTerm" LIMIT=10 python -m app.jobs.user_lookups
```

Lookup tweet timelines, specifying the max number of users to fetch, and the max number of tweets per user:

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.jobs.timeline_lookups
```

Lookup friends, specifying the max number of users to fetch, and the max number of friends per user:

```sh
USER_LIMIT=100 FRIEND_LIMIT=10_000 python -m app.jobs.friend_lookups
```

Lookup followers, specifying the max number of users to fetch, and the max number of followers per user:

```sh
USER_LIMIT=100 FOLLOWER_LIMIT=10_000 python -m app.jobs.follower_lookups
```


Continuous collection of tweet timelines, specifying the max number of users to fetch, and the max number of tweets per user (it also uses their last tweet id if we have it):

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.jobs.timeline_collection
```


## Testing

Run tests:

```sh
pytest
```

## [Deploying](DEPLOYING.md)

## [License](LICENSE.md)
