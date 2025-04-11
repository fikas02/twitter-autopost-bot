import tweepy
import os
import datetime
import random
import logging
from dotenv import load_dotenv  # Untuk local testing

# ===== Setup Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ===== Konfigurasi =====
class Config:
    RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun yaa"
    OTHER_MESSAGES = [
        "Aku onn",
        "Bismillah 🤲 Sehat & rezeki melimpah ✨",
        "Aku open ress",
        "off dulss gaiss",
        "Jangan lupa follow @xiaojdun untuk update terbaru!",
        "Pagi semangat! Jangan lupa minum air putih 💧"
    ]
    TOLERANCE_MINUTES = 10  # Toleransi delay posting (menit)

# ===== Inisialisasi Twitter Client =====
def initialize_twitter_client():
    try:
        # Load .env untuk local testing (opsional)
        load_dotenv()
        
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
        logger.error(f"❌ Gagal koneksi Twitter: {e}")
        raise

# ===== Generate Jadwal =====
def generate_daily_schedule():
    """Generate jadwal dengan:
    - 2x fixed time (03:00 & 15:00 UTC)
    - 3x random time (16:00-20:00 UTC, menit 0/30)
    """
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,  # 10:00 WIB
        "15:00": Config.RESELLER_MESSAGE   # 22:00 WIB
    }

    # Tambahkan 3 tweet acak antara 16:00-20:00 UTC
    for _ in range(3):
        hour = random.randint(16, 20)
        minute = random.choice([0, 30])  # Sesuai cron job
        schedule[f"{hour:02d}:{minute:02d}"] = random.choice(Config.OTHER_MESSAGES)
    
    return schedule

# ===== Posting Tweet =====
def post_tweet(client, message):
    try:
        response = client.create_tweet(text=message)
        tweet_url = f"https://twitter.com/user/status/{response.data['id']}"
        logger.info(f"✅ Tweet terkirim: {tweet_url}")
        return True
    except tweepy.TweepyException as e:
        logger.error(f"❌ Gagal posting: {e}")
        return False

# ===== Cek Waktu dengan Toleransi =====
def is_time_match(current_time, scheduled_time, tolerance=10):
    """Cek apakah current_time dalam toleransi scheduled_time"""
    fmt = "%H:%M"
    current = datetime.datetime.strptime(current_time, fmt)
    scheduled = datetime.datetime.strptime(scheduled_time, fmt)
    delta = abs((current - scheduled).total_seconds()) / 60  # Dalam menit
    return delta <= tolerance

# ===== Fungsi Utama =====
def main():
    logger.info("\n=== BOT DIMULAI ===")
    
    # 1. Inisialisasi Twitter Client
    client = initialize_twitter_client()
    
    # 2. Generate Jadwal
    schedule = generate_daily_schedule()
    logger.info("📅 Jadwal Hari Ini:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:50]}...")  # Tampilkan 50 karakter pertama

    # 3. Cek Waktu Sekarang
    current_time = datetime.datetime.utcnow().strftime("%H:%M")
    logger.info(f"🕒 Waktu Sekarang (UTC): {current_time}")

    # 4. Cek dan Posting
    posted = False
    for scheduled_time, message in schedule.items():
        if is_time_match(current_time, scheduled_time, Config.TOLERANCE_MINUTES):
            logger.info(f"🎯 Menemukan jadwal: {scheduled_time} UTC (dalam toleransi ±{Config.TOLERANCE_MINUTES} menit)")
            if post_tweet(client, message):
                posted = True
                break  # Hanya post 1 tweet per eksekusi

    if not posted:
        logger.info("⏳ Tidak ada jadwal yang cocok")

    logger.info("=== BOT SELESAI ===\n")

if __name__ == "__main__":
    main()
