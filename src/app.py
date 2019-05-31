from datetime import date, datetime, timedelta
from os import getenv
from time import sleep

import logging
import re

import praw

# setup logging
logger = logging.getLogger("daily_discussion_helper")
logger.setLevel(logging.DEBUG)

# constants
AUTOMODERATOR = "AutoModerator"
VERSION = "0.0.3"

# regex
TITLE_REGEX = re.compile(r'title: "(.*)"')
DATE_REGEX = re.compile(r'{{date (.*)}}')
FIRST_REGEX = re.compile(r'first: "(.*)"')
FIRST_AND_VALUE_REGEX = re.compile(r'first: "\d*/\d/\d* \d:\d* \D\D"')


class DailyDiscussionHelper:
    def __init__(self, reddit, subreddit_name):
        logger.info(f"Daily Discussion Helper Tool - Version {VERSION}")
        self.reddit = reddit
        self.subreddit_name = subreddit_name
        self.subreddit = self.reddit.subreddit(subreddit_name)
        self.fetch_automoderator_schedule()

    def fetch_automoderator_schedule(self):
        logger.info("Fetching automoderator_schedule")
        # TODO: add some error handling here, basically retry or quit.
        self.automoderator_schedule = self.subreddit.wiki["automoderator-schedule"]
        logger.info("Fetched automoderator_schedule")
        logger.debug(self.automoderator_schedule.content_md)
        self._parse_automoderator_schedule(self.automoderator_schedule.content_md)

    def _parse_automoderator_schedule(self, schedule):
        logger.info("Parsing automoderator_schedule")
        self.title_format = TITLE_REGEX.search(schedule).group(1)
        logger.info(f"title_format: {self.title_format}")
        self.title_date_format = DATE_REGEX.search(self.title_format).group(1)
        logger.info(f"title_date_format: {self.title_date_format}")
        self.first_datetime = FIRST_REGEX.search(schedule).group(1)
        logger.info(f"first_datetime: {self.first_datetime}")
        logger.info("Parsed automoderator schedule.")

    def _update_automoderator_schedule(self, first_datetime, reason):
        logger.info("Updating first_run datetime")
        first_datetime_formatted = first_datetime.strftime("%d/%-m/%Y %I:%M %p")
        logger.info(f"Updated first_run datetime to: {first_datetime_formatted}")
        content = FIRST_AND_VALUE_REGEX.sub(
            f'first: "{first_datetime_formatted}"',
            self.automoderator_schedule.content_md,
        )
        print(content, reason)
        # TODO: enable uploading, possibly have a DEBUG env for development.
        logger.info('Uploading switched off in _update_automoderator_schedule() function.')
        # self._upload_automoderator_schedule(content, reason)

    def _upload_automoderator_schedule(self, content, reason):
        logger.info("Uploading automoderator_schedule and sending update message")
        response = self.automoderator_schedule.edit(content=content, reason=reason)
        logger.info("Uploaded automoderator_schedule, sending update message")
        self.reddit.redditor(AUTOMODERATOR).message(self.subreddit_name, "schedule")
        logger.info(f"Sent schedule update message to {AUTOMODERATOR}")
        return response
    
    def _daily_discussion_title_to_date(self, title):
        # TODO: should we just use the date the daily discussion was posted?
        return datetime.strptime(title.split(" - ")[1], self.title_date_format.replace('-', ''))

    def _is_daily_discussion(self, submission):
        if submission.author.name == AUTOMODERATOR:
            # TODO: we should parse title_format properly on the next line
            if submission.title.startswith(self.title_format.split(" - ")[0]):
                return True
        return False

    def _scan_for_latest_daily_discussion(self, limit=1000):
        logger.info(f"Scanning latest {limit} submissions on /r/{self.subreddit_name}")
        # look through the newest posts until we hit limit.
        for submission in self.subreddit.new(limit=limit):
            if self._is_daily_discussion(submission):
                logger.debug('Scan complete, found daily.')
                return submission
        logger.info('Scan complete, could not find daily.')
        return None
    
    def check(self):
        latest_daily = self._scan_for_latest_daily_discussion()
        if latest_daily:
            logger.info(f'Found thread: {latest_daily.title}')
            latest_daily_date = self._daily_discussion_title_to_date(latest_daily.title)
            logger.info(f'Daily date from title: {latest_daily_date}')
            latest_daily_created = latest_daily.created_utc
            logger.info(f'Daily was posted at: {latest_daily_created}')
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            if latest_daily_date.date() == today.date():
                logger.info(f'Daily is for: today.')
                # TODO: potentially run stickyfix here, may also want to fix yesterday though.
            elif latest_daily_date.date() == yesterday.date():
                logger.info(f'Daily is for: yesterday.')
                # TODO: check it is 5 minutes after start_time, if daily should have posted run the fix
        # TODO: this should return whether the checks have been successful or not
        return False


if __name__ == "__main__":
    # setup logging handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # this is additional debug logging for PRAW
    praw_logger = logging.getLogger("prawcore")
    praw_logger.setLevel(logging.DEBUG)
    praw_logger.addHandler(handler)

    # create an authenticated reddit client
    reddit = praw.Reddit(
        client_id=getenv("CLIENT_ID"),
        client_secret=getenv("CLIENT_SECRET"),
        user_agent=getenv("USER_AGENT"),
        username=getenv("USERNAME"),
        password=getenv("PASSWORD"),
    )

    # setup daily_discussion_helper object and pass in authenticated reddit client
    daily_discussion_helper = DailyDiscussionHelper(reddit, getenv("SUBREDDIT"))
    success = daily_discussion_helper.check()
    logger.info(f'Check completed: {success}')
