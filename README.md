Ethtrader Daily Discussion Fix
==============================

This script when run with moderator permissions is capable of fixing two classes of issues that we have had with Daily Discussions on /r/ethtrader

1. Daily Discussion not being posted at all, particularly if Reddit is down for maintenance when tasks should be run.
2. The Daily Discussion for the correct day not being stickied.

Setup
-----

First of all you need to setup an .env file (or use environment variables directly) with the required settings:

```sh
cp .env.example .env
vi .env
```

Make sure you fill out all the required fields including USER_AGENT.

Run
---

Now you can run the script using docker-compose

```sh
docker-compose up
```

If you'd prefer not to use docker that is also fine, the script can be installed and run directly:

```sh
pipenv install
pipenv run python3 src/app.py
```

You must have Python 3.7 installed on your machine to run the script in this way.