# tweet-analysis-2021

This is a fresh start follow-up to some [previous research code](https://github.com/s2t2/tweet-analyzer-py).

The goal of this repo is to provide shared code for local dev, Heroku server, and Google Colab environments.

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

### Environment Variables

Create a new file in the root directory of this repo called ".env", and set your environment variables there, as necessary:

```sh
# example .env file

GOOGLE_APPLICATION_CREDENTIALS="/path/to/tweet-analysis-2021/google-credentials.json"

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

Lookup user information:

```sh
SEARCH_TERM="#WWG1WGA" LIMIT=10 python -m app.jobs.user_lookups
```

Lookup tweet timelines:

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.jobs.timeline_lookups
```

## [Deploying](DEPLOYING.md)
