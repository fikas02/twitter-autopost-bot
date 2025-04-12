import tweepy
import os
import datetime
import json
import random
import logging
from pathlib import Path

# ===== Setup =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bot.log")]
)
logger = logging.getLogger(__name__)

class Config:
    RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak!..."
    OTHER_MESSAGES = ["Aku onn", "Bismillah 🤲", "off dulss gaiss"]
    SCHEDULE_FILE = "schedule_history.json"
    CHECK_INTERVAL = 15  # Menit

# ===== Twitter Client =====
def get_twitter_client():
    return tweepy.Client(
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )

# ===== Jadwal & History =====
def generate_daily_schedule():
    """Generate jadwal hari ini + simpan ke file"""
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,
        "15:00": Config.RESELLER_MESSAGE,
        **{f"{random.randint(16,20)}:{random.choice([0,30])}": random.choice(Config.OTHER_MESSAGES) for _ in range(3)}
    }
    
    # Simpan jadwal
    history = load_history()
    history["schedule"] = schedule
    history["generated_at"] = datetime.datetime.utcnow().isoformat()
    save_history(history)
    
    return schedule

def load_history():
    try:
        with open(Config.SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedule": {}, "generated_at": None, "posted": []}

def save_history(data):
    with open(Config.SCHEDULE_FILE, "w") as f:
        json.dump(data, f)

# ===== Posting Logic =====
def should_post(schedule_time, history):
    """Cek apakah harus posting"""
    now = datetime.datetime.utcnow()
    scheduled_time = datetime.datetime.strptime(schedule_time, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    
    # Cek dalam rentang 15 menit
    time_diff = abs((now - scheduled_time).total_seconds()) / 60
    is_time_match = time_diff <= Config.CHECK_INTERVAL
    
    # Cek apakah sudah pernah posting
    is_posted = schedule_time in history.get("posted", [])
    
    # Cek apakah jadwal sudah lewat (dalam 12 jam terakhir)
    is_past_due = (now - scheduled_time).total_seconds() <= 12 * 3600
    
    return (is_time_match or is_past_due) and not is_posted

def post_tweet(client, message, schedule_time):
    try:
        client.create_tweet(text=message)
        logger.info(f"✅ Posted: {schedule_time} UTC")
        
        # Update history
        history = load_history()
        history["posted"].append(schedule_time)
        save_history(history)
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to post: {e}")
        return False

# ===== Main Function =====
def main():
    logger.info("\n==== BOT STARTED ====")
    
    # 1. Load/Muat Jadwal
    history = load_history()
    if not history.get("schedule") or datetime.datetime.fromisoformat(history["generated_at"]).date() != datetime.datetime.utcnow().date():
        schedule = generate_daily_schedule()
    else:
        schedule = history["schedule"]
    
    logger.info("📅 Today's Schedule:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:30]}...")

    # 2. Cek dan Posting
    client = get_twitter_client()
    for schedule_time, message in schedule.items():
        if should_post(schedule_time, history):
            logger.info(f"🎯 Processing: {schedule_time} UTC")
            post_tweet(client, message, schedule_time)
    
    logger.info("==== BOT FINISHED ====\n")

if __name__ == "__main__":
    main()
