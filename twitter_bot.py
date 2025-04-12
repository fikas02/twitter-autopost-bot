import tweepy
import os
import datetime
import random
import logging
from collections import defaultdict

# ===== Setup =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class Config:
    RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh..."
    OTHER_MESSAGES = [
        "Aku onn", "Bismillah 🤲", "Aku open ress", 
        "off dulss gaiss", "Follow @xiaojdun", "Minum air putih 💧"
    ]
    TOLERANCE_MINUTES = 15  # Diperlebar dari 10 menit
    MAX_RETRIES = 3

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
        logger.info(f"✅ Terhubung ke Twitter sebagai @{user.data.username}")
        return client
    except Exception as e:
        logger.error(f"❌ Gagal koneksi: {e}")
        raise

def generate_daily_schedule():
    """Generate jadwal dengan pesan unik dan waktu acak."""
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,
        "15:00": Config.RESELLER_MESSAGE
    }
    
    # Pastikan pesan acak tidak duplikat
    available_messages = Config.OTHER_MESSAGES.copy()
    random.shuffle(available_messages)
    
    for i in range(3):  # 3 tweet acak
        hour = random.randint(16, 20)
        minute = random.choice([0, 30])
        time_key = f"{hour:02d}:{minute:02d}"
        
        if i < len(available_messages):
            schedule[time_key] = available_messages[i]
        else:
            schedule[time_key] = random.choice(Config.OTHER_MESSAGES)
    
    return schedule

def post_tweet(client, message, retry=0):
    try:
        response = client.create_tweet(text=message)
        logger.info(f"✅ Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        if retry < Config.MAX_RETRIES:
            logger.warning(f"⚠️ Coba lagi ({retry+1}/{Config.MAX_RETRIES})...")
            time.sleep(5)
            return post_tweet(client, message, retry+1)
        logger.error(f"❌ Gagal posting setelah {Config.MAX_RETRIES} percobaan: {e}")
        return False

def main():
    logger.info("\n=== BOT DIMULAI ===")
    client = initialize_twitter_client()
    schedule = generate_daily_schedule()
    
    # Log jadwal
    logger.info("📅 Jadwal Hari Ini:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:50]}...")

    # Cek waktu dengan toleransi
    current_time = datetime.datetime.utcnow()
    current_str = current_time.strftime("%H:%M")
    logger.info(f"🕒 Waktu Sekarang (UTC): {current_str}")

    posted = False
    for scheduled_time, message in schedule.items():
        scheduled = datetime.datetime.strptime(scheduled_time, "%H:%M")
        delta = abs((current_time - scheduled).total_seconds()) / 60  # Menit
        
        if delta <= Config.TOLERANCE_MINUTES:
            logger.info(f"🎯 Menemukan jadwal: {scheduled_time} UTC (±{Config.TOLERANCE_MINUTES} menit)")
            if post_tweet(client, message):
                posted = True
                break

    if not posted:
        logger.info("⏳ Tidak ada jadwal yang cocok")
    logger.info("=== BOT SELESAI ===\n")

if __name__ == "__main__":
    main()
