# Deploying to Heroku

## Server Setup

Create a new app server (first time only):

```sh
heroku create tweet-analysis-2021 # (use your own app name here)
```

## Server Config

Provision and configure the Google Application Credentials Buildpack to generate a credentials file on the server:

```sh
heroku buildpacks:set heroku/python
heroku buildpacks:add https://github.com/s2t2/heroku-google-application-credentials-buildpack
heroku config:set GOOGLE_CREDENTIALS="$(< google-credentials.json)" # references local creds file
heroku config:set GOOGLE_APPLICATION_CREDENTIALS="google-credentials.json" # references server creds
```

Configure the rest of the environment variables:

```sh
heroku config:set APP_ENV="production"

heroku config:set DATASET_ADDRESS="tweet-collector-py.disinfo_2021_production"

heroku config:set TWITTER_API_KEY="_____________"
heroku config:set TWITTER_API_KEY_SECRET="_____________"
heroku config:set TWITTER_ACCESS_TOKEN="_____________"
heroku config:set TWITTER_ACCESS_TOKEN_SECRET="_____________"
```





## Deployment

Deploy:

```sh
# from the main branch:
git push heroku main

# from another branch (like my-branch):
git push heroku my-branch:main
```

## Running Jobs

Set any environment variables as required by the job, add the job's execution command to the "Procfile", then setup a Heroku "dyno" (hobby tier) to run it.

Checking logs:

```sh
heroku logs --ps my_job
```
