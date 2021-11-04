import concurrent.futures
import itertools
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from threading import Thread, Lock
from typing import Union, Generator, Any, NoReturn, Dict

import praw
from praw.exceptions import PRAWException
from praw.models import Comment, Submission
from praw.models.util import stream_generator
from prawcore.exceptions import PrawcoreException
from pymongo import MongoClient

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

SUBREDDITS = ("wallstreetbets",)

DB_NAME = "WSB-data"
DB_COLLECTION = "historical-data"

MAX_QUEUED_JOBS = 64

singleton_lock = Lock()


class StreamType(Enum):
    SUBMISSIONS = auto()
    COMMENTS = auto()


# Taken from https://stackoverflow.com/questions/50566934/why-is-this-singleton-implementation-not-thread-safe
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with singleton_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MongoDB(MongoClient, metaclass=Singleton):
    def __init__(self):
        super().__init__(
            host=os.environ["MONGODB_SERVICE_HOST"],
            port=int(os.environ["MONGODB_SERVICE_PORT"]),
            username=os.environ["MONGO_ROOT_USERNAME"],
            password=os.environ["MONGO_ROOT_PASSWORD"],
            authSource="admin"
        )


def get_stream(subreddit: praw.reddit.Subreddit, stream_type: StreamType, **stream_options: Any) \
        -> Generator[Union[Submission, Comment], None, None]:
    if stream_type is StreamType.COMMENTS:
        return stream_generator(subreddit.comments, **stream_options)
    elif stream_type is StreamType.SUBMISSIONS:
        return stream_generator(subreddit.new, **stream_options)


def content_to_json(content: Union[Submission, Comment]) -> Dict:
    if isinstance(content, Submission):
        fields = (
            "title", "selftext", "score", "created_utc", "num_comments", "distinguished", "id", "over_18", "ups",
            "stickied", "upvote_ratio",  "total_awards_received", "downs", "gilded", "num_crossposts", "num_duplicates"
        )
    elif isinstance(content, Comment):
        fields = (
            "score", "body", "created_utc", "distinguished", "id", "link_id", "parent_id", "stickied", "gilded",
            "controversiality", "downs", "total_awards_received", "ups"
        )

    content_json = vars(content)

    return {field: content_json[field] for field in fields if field in content_json}


def process_content(content: Union[Submission, Comment], reddit: praw.Reddit = None) -> None:
    if reddit is None:
        reddit = praw.Reddit(
            client_id=os.environ.get("CLIENT_ID"),
            client_secret=os.environ.get("CLIENT_SECRET"),
            user_agent="linux:hivemind:v0.1 (by u/stuepid)"
        )

    db_client = MongoDB()
    db_collection = db_client[DB_NAME][DB_COLLECTION]

    if isinstance(content, Submission):
        # Insert/update submission in DB
        db_collection.update_one({"id": content.id}, {"$set": content_to_json(content)}, upsert=True)
    elif isinstance(content, Comment):
        # Does the comment's parent post exist in the DB?
        if not db_collection.count_documents({"id": content.link_id[3:]}, limit=1):
            # If not, get that post and insert it
            parent_submission = Submission(reddit, id=content.link_id[3:])
            process_content(parent_submission, reddit)

            # Add the comment to the newly inserted post
            db_collection.update_one(
                {"id": content.link_id[3:]},
                {"$addToSet": {"comments": content_to_json(content)}}
            )
        else:
            # Check if comment exists in parent post's list of comments
            if db_collection.count_documents({"id": content.link_id[3:], "comments.id": content.id}, limit=1):
                # Update the comment -- NOTE this actually replaces the entire comment
                db_collection.update_one(
                    {"id": content.link_id[3:], "comments.id": content.id},
                    {"$set": {"comments.$": content_to_json(content)}}
                )
            else:
                # Push the comment to the array otherwise
                db_collection.update_one(
                    {"id": content.link_id[3:]},
                    {"$addToSet": {"comments": content_to_json(content)}}
                )

        # If the comment has a parent comment, process it and walk up the chain
        if content.parent_id.startswith("t1_"):
            process_content(Comment(reddit, content.parent_id[3:]), reddit)


def stream_content(subreddit_name: str, stream_type: StreamType) -> NoReturn:
    # As per the PRAW documentation, each thread needs its own unique instance of the Reddit object
    reddit = praw.Reddit(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        user_agent="linux:hivemind:v0.1 (by u/stuepid)"
    )

    subreddit = reddit.subreddit(subreddit_name)

    # Executor logic adapted from https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/
    with ThreadPoolExecutor() as executor:
        # Discussion on best practices for the PRAW streaming implementation:
        # https://github.com/praw-dev/praw/issues/1025
        while True:
            try:
                # The stream needs recreated in the case of an error
                # Use the `get_stream` function to do so in a generic way
                content_stream = get_stream(subreddit, stream_type, pause_after=None, skip_existing=False)

                # Submit MAX_QUEUED_JOBS to initially be processed
                futures = {
                    executor.submit(process_content, content)
                    for content in itertools.islice(content_stream, MAX_QUEUED_JOBS)
                }

                while futures:
                    # Wait for the next task to complete
                    done, futures = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

                    # Schedule the next set of jobs. Since our processing logic is slower than the time it takes to
                    # stream a new piece of content we want to ensure the pool only ever has MAX_QUEUED_JOBS to avoid a
                    # gradual memory overrun
                    for content in itertools.islice(content_stream, len(done)):
                        futures.add(executor.submit(process_content, content))

            except (PRAWException, PrawcoreException) as e:
                print(e)


def main():
    for sub in SUBREDDITS:
        # Each stream is an infinite generator, so to ensure we can process multiple streams simultaneously this needs
        # to be threaded
        submissions_thread = Thread(target=stream_content, args=(sub, StreamType.SUBMISSIONS))
        comments_thread = Thread(target=stream_content, args=(sub, StreamType.COMMENTS))

        submissions_thread.start()
        comments_thread.start()

        submissions_thread.join()
        comments_thread.join()


if __name__ == '__main__':
    logging.info('starting reddit-producer')
    main()
