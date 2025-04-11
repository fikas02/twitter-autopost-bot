import tweepy
import os
import datetime
import json
import random
import logging

# ===== Setup Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ===== Konfigurasi =====
class Config:
    LAST_POST_FILE = "last_post.json"
    RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun yaa"
    OTHER_MESSAGES = [
        "Aku onn",
        "Bismillah 🤲 Sehat & rezeki melimpah ✨",
        "Aku open ress",
        "off dulss gaiss",
        "Jangan lupa follow @xiaojdun untuk update terbaru!",
        "Pagi semangat! Jangan lupa minum air putih 💧"
    ]

# ===== Inisialisasi Twitter Client =====
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
        logger.info(f"Terhubung ke Twitter sebagai @{user.data.username}")
        return client
    except Exception as e:
        logger.error(f"Gagal koneksi: {e}")
        raise

# ===== Manajemen Jadwal =====
def generate_daily_schedule():
    """Generate jadwal untuk hari ini."""
    schedule = {
        "15:00": Config.RESELLER_MESSAGE,  # 22:00 WIB
        "03:00": Config.RESELLER_MESSAGE    # 10:00 WIB
    }

    # Tambahkan 3 tweet acak antara 16:00-20:00 UTC (23:00-03:00 WIB)
    for _ in range(3):
        hour = random.randint(16, 20)
        minute = random.choice([0, 30])  # Sesuai cron job (setiap 30 menit)
        schedule[f"{hour:02d}:{minute:02d}"] = random.choice(Config.OTHER_MESSAGES)

    return schedule

# ===== Posting Tweet =====
def post_tweet(client, message):
    try:
        response = client.create_tweet(text=message)
        logger.info(f"Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        logger.error(f"Gagal posting: {e}")
        return False

# ===== Fungsi Utama =====
def main():
    client = initialize_twitter_client()
    schedule = generate_daily_schedule()
    current_time = datetime.datetime.utcnow().strftime("%H:%M")

    logger.info(f"Memeriksa jadwal (UTC: {current_time})")

    # Cek apakah waktu saat ini ada di jadwal
    if current_time in schedule:
        message = schedule[current_time]
        if post_tweet(client, message):
            logger.info("Bot selesai berjalan.")
        else:
            logger.warning("Gagal posting, coba lagi nanti.")
    else:
        logger.info(f"Tidak ada jadwal untuk {current_time} UTC.")

if __name__ == "__main__":
    main()
