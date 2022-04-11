
# Data Collection

## Jobs / Worker Processes

We start by collecting tweets in real-time using a Stream Listener approach. Then we follow-up with a historic collection of tweets for selected users, using the Search API.

### Twitter Stream Listener

Use the ["tweet_collection_v2" code](https://github.com/s2t2/tweet-analyzer-py/tree/master/app/tweet_collection_v2) from the previous repo to collect tweets mentioning one of a number of specified terms.

> TODO: copy the stream listener code into this repository...

### Twitter Search API

Lookup user information, for users in our dataset who tweeted using a specified search term, optionally specifying a max number of users to fetch:

```sh
SEARCH_TERM="#MySearchTerm" LIMIT=10 python -m app.data_collection.user_lookups
```

Lookup tweet timelines, specifying the max number of users to fetch, and the max number of tweets per user:

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.data_collection.timeline_lookups
```

Lookup friends, specifying the max number of users to fetch, and the max number of friends per user:

```sh
USER_LIMIT=100 FRIEND_LIMIT=10_000 python -m app.data_collection.friend_lookups
```

Lookup followers, specifying the max number of users to fetch, and the max number of followers per user:

```sh
USER_LIMIT=100 FOLLOWER_LIMIT=10_000 python -m app.data_collection.follower_lookups
```


Continuous collection of tweet timelines, specifying the max number of users to fetch, and the max number of tweets per user (it also uses their last tweet id if we have it):

```sh
USER_LIMIT=3 STATUS_LIMIT=5_000 python -m app.data_collection.timeline_collection
```
