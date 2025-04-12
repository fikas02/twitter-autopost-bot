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
    RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh..."
    OTHER_MESSAGES = [
        "Aku onn",
        "Bismillah 🤲 Sehat & rezeki melimpah ✨", 
        "Aku open ress",
        "off dulss gaiss",
        "Jangan lupa follow @xiaojdun!"
    ]
    SCHEDULE_FILE = "schedule_history.json"
    CHECK_INTERVAL = 30  # Toleransi 30 menit
    POST_INTERVAL = 6 * 3600  # Batas duplikasi: 6 jam

def get_twitter_client():
    return tweepy.Client(
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )

def generate_daily_schedule():
    """Generate jadwal dengan pesan acak"""
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,
        "15:00": Config.RESELLER_MESSAGE
    }
    
    # Tambahkan 3 slot acak (16:00-20:00 UTC)
    for _ in range(3):
        hour = random.randint(16, 20)
        minute = random.choice([0, 30])
        schedule[f"{hour:02d}:{minute:02d}"] = random.choice(Config.OTHER_MESSAGES)
    
    return schedule

def load_history():
    try:
        with open(Config.SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedule": {}, "posted": []}

def save_history(data):
    with open(Config.SCHEDULE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def should_post(schedule_time, message, history):
    """Cek apakah harus posting"""
    # 1. Cek apakah sudah pernah diposting di jadwal ini
    if any(entry["schedule_time"] == schedule_time for entry in history.get("posted", [])):
        return False
    
    # 2. Cek duplikasi konten dalam 6 jam
    last_similar = max(
        (datetime.datetime.fromisoformat(entry["time"]) for entry in history.get("posted", [])
        if entry["message"] == message
    ), default=None)
    
    return (not last_similar) or ((datetime.datetime.utcnow() - last_similar).total_seconds() > Config.POST_INTERVAL)

def main():
    logger.info("\n==== BOT STARTED ====")
    
    # 1. Load/Muat Jadwal
    history = load_history()
    if not history.get("schedule") or datetime.datetime.utcnow().date() != datetime.datetime.fromisoformat(history.get("generated_at", "1970-01-01")).date():
        history["schedule"] = generate_daily_schedule()
        history["generated_at"] = datetime.datetime.utcnow().isoformat()
        save_history(history)
    
    schedule = history["schedule"]
    logger.info("📅 Today's Schedule:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:30]}...")

    # 2. Proses Posting
    client = get_twitter_client()
    posted_count = 0
    
    for schedule_time, message in schedule.items():
        try:
            scheduled_time = datetime.datetime.strptime(schedule_time, "%H:%M").replace(
                year=datetime.datetime.utcnow().year,
                month=datetime.datetime.utcnow().month,
                day=datetime.datetime.utcnow().day
            )
            time_diff = abs((datetime.datetime.utcnow() - scheduled_time).total_seconds() / 60
            
            if time_diff <= Config.CHECK_INTERVAL and should_post(schedule_time, message, history):
                logger.info(f"🎯 Processing: {schedule_time} UTC")
                response = client.create_tweet(text=message)
                logger.info(f"✅ Posted: {response.data['id']}")
                
                history["posted"].append({
                    "time": datetime.datetime.utcnow().isoformat(),
                    "message": message,
                    "schedule_time": schedule_time
                })
                posted_count += 1
                
        except tweepy.TweepyException as e:
            logger.error(f"❌ Failed to post {schedule_time}: {e}")
        except Exception as e:
            logger.error(f"⚠️ Unexpected error: {e}")
    
    save_history(history)
    logger.info(f"Total posted today: {posted_count}")
    logger.info("==== BOT FINISHED ====\n")

if __name__ == "__main__":
    main()
