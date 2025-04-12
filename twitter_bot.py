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
    CHECK_INTERVAL = 15  # Menit
    POST_INTERVAL = 4 * 3600  # 4 jam (minimal interval untuk konten sama)

def get_twitter_client():
    return tweepy.Client(
        consumer_key=os.getenv("API_KEY"),
        consumer_secret=os.getenv("API_SECRET"),
        access_token=os.getenv("ACCESS_TOKEN"),
        access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )

def generate_daily_schedule():
    """Generate jadwal dengan konten unik"""
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,
        "15:00": Config.RESELLER_MESSAGE
    }
    
    used_messages = set()
    available_messages = Config.OTHER_MESSAGES.copy()
    
    for _ in range(3):
        while True:
            hour = random.randint(16, 20)
            minute = random.choice([0, 30])
            time_key = f"{hour:02d}:{minute:02d}"
            
            if not available_messages:
                available_messages = Config.OTHER_MESSAGES.copy()
                used_messages.clear()
                
            message = random.choice(available_messages)
            available_messages.remove(message)
            used_messages.add(message)
            
            schedule[time_key] = message
            break
            
    return schedule

def load_history():
    try:
        with open(Config.SCHEDULE_FILE, "r") as f:
            data = json.load(f)
            # Clean old entries (older than 24 hours)
            current_time = datetime.datetime.utcnow()
            data["posted"] = [
                entry for entry in data.get("posted", [])
                if (current_time - datetime.datetime.fromisoformat(entry["time"])).total_seconds() < 24 * 3600
            ]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"schedule": {}, "generated_at": None, "posted": []}

def save_history(data):
    with open(Config.SCHEDULE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def can_post_message(message, history):
    """Cek apakah pesan boleh diposting (tidak duplicate dalam 4 jam)"""
    last_posted = [
        entry["time"] for entry in history.get("posted", [])
        if entry["message"] == message
    ]
    if not last_posted:
        return True
        
    last_time = max(datetime.datetime.fromisoformat(t) for t in last_posted)
    return (datetime.datetime.utcnow() - last_time).total_seconds() > Config.POST_INTERVAL

def main():
    logger.info("\n==== BOT STARTED ====")
    
    # 1. Load/Muat Jadwal
    history = load_history()
    if not history.get("schedule") or datetime.datetime.fromisoformat(history["generated_at"]).date() != datetime.datetime.utcnow().date():
        logger.info("Generating new schedule for today")
        history["schedule"] = generate_daily_schedule()
        history["generated_at"] = datetime.datetime.utcnow().isoformat()
        save_history(history)
    
    schedule = history["schedule"]
    logger.info("📅 Today's Schedule:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:30]}...")

    # 2. Cek dan Posting
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
            
            if time_diff <= Config.CHECK_INTERVAL and can_post_message(message, history):
                logger.info(f"Attempting to post: {schedule_time} UTC")
                response = client.create_tweet(text=message)
                logger.info(f"✅ Posted: {schedule_time} UTC - Tweet ID: {response.data['id']}")
                
                history["posted"].append({
                    "time": datetime.datetime.utcnow().isoformat(),
                    "message": message,
                    "schedule_time": schedule_time
                })
                posted_count += 1
                
        except tweepy.TweepyException as e:
            logger.error(f"❌ Failed to post {schedule_time}: {str(e)}")
        except Exception as e:
            logger.error(f"⚠️ Unexpected error: {str(e)}")
    
    save_history(history)
    logger.info(f"Posted {posted_count} tweets today")
    logger.info("==== BOT FINISHED ====\n")

if __name__ == "__main__":
    main()
