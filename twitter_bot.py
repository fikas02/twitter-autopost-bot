import tweepy
import os
import datetime
import json
import time
import random
import signal
import logging
from filelock import FileLock

# ===== Setup Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("twitter_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== Configuration =====
class Config:
    SCHEDULE_FILE = "schedule.json"
    LAST_POST_FILE = "last_post.json"
    LOCK_FILE = "bot.lock"
    MAX_RETRIES = 3
    RETRY_DELAY = 60  # seconds

# ===== Twitter Client =====
def initialize_twitter_client():
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("API_KEY"),
            consumer_secret=os.getenv("API_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
            wait_on_rate_limit=True
        )
        user = client.get_me()
        logger.info(f"Connected to Twitter as @{user.data.username}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        raise

# ===== Schedule Management =====
def generate_schedule():
    RESELLER_MESSAGE = "OPEN RESELLER! ..."
    OTHER_MESSAGES = ["Aku onn", "Bismillah ...", ...]

    schedule = {
        "15:00": RESELLER_MESSAGE,
        "03:00": RESELLER_MESSAGE
    }

    # Add random night posts (16:00-20:00 UTC)
    for _ in range(3):
        hour = random.randint(16, 20)
        minute = random.randint(0, 59)
        schedule[f"{hour:02d}:{minute:02d}"] = random.choice(OTHER_MESSAGES)

    # Add 3 random posts at other times
    for _ in range(3):
        while True:
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            time_key = f"{hour:02d}:{minute:02d}"
            if time_key not in schedule:
                schedule[time_key] = random.choice(OTHER_MESSAGES)
                break

    return schedule

def load_schedule():
    try:
        with open(Config.SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        schedule = generate_schedule()
        with open(Config.SCHEDULE_FILE, "w") as f:
            json.dump(schedule, f)
        return schedule

# ===== Anti-Duplication =====
def save_last_post(time_key):
    with FileLock(Config.LAST_POST_FILE + ".lock"):
        with open(Config.LAST_POST_FILE, "w") as f:
            json.dump({
                "last_post": time_key,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }, f)

def load_last_post():
    try:
        with FileLock(Config.LAST_POST_FILE + ".lock"):
            with open(Config.LAST_POST_FILE, "r") as f:
                data = json.load(f)
                post_time = datetime.datetime.fromisoformat(data["timestamp"])
                if (datetime.datetime.utcnow() - post_time).total_seconds() >= 12 * 3600:
                    return None
                return data.get("last_post")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None
    except Exception as e:
        logger.error(f"Error loading last_post: {e}")
        return None

# ===== Tweet Posting =====
def post_tweet(client, message, retry=0):
    try:
        response = client.create_tweet(text=message)
        logger.info(f"Tweet posted: https://twitter.com/user/status/{response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        logger.error(f"Failed to post (Tweepy): {e}")
        if retry < Config.MAX_RETRIES:
            time.sleep(Config.RETRY_DELAY * (retry + 1))
            return post_tweet(client, message, retry + 1)
        return False

# ===== Main Loop =====
def main():
    client = initialize_twitter_client()
    schedule = load_schedule()
    last_schedule_day = datetime.datetime.utcnow().day

    def shutdown_handler(signum, frame):
        logger.info("Shutting down gracefully...")
        exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    while True:
        try:
            current_time = datetime.datetime.utcnow()
            if current_time.day != last_schedule_day:
                schedule = generate_schedule()
                last_schedule_day = current_time.day
                logger.info("Generated new schedule for the day")

            current_hour_min = current_time.strftime("%H:%M")
            last_post = load_last_post()

            for schedule_time, message in schedule.items():
                schedule_hour, schedule_min = map(int, schedule_time.split(":"))
                if (current_time.hour == schedule_hour and 
                    (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)):
                    if last_post != schedule_time:
                        if post_tweet(client, message):
                            save_last_post(schedule_time)
                            time.sleep(60)  # Avoid rapid consecutive posts
                    break

            time.sleep(300 - (time.time() % 300))  # Precise 5-minute sleep

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
