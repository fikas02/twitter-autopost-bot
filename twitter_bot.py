import tweepy
import os
import datetime
import random
import logging
import time

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
    TOLERANCE_MINUTES = 30  # Toleransi delay diperlebar (30 menit)
    MAX_RETRIES = 2  # Maksimal retry jika gagal posting

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
        logger.info(f"✅ Terhubung ke Twitter sebagai @{user.data.username}")
        return client
    except Exception as e:
        logger.error(f"❌ Gagal koneksi: {e}")
        raise

# ===== Generate Jadwal (Boleh Duplikasi Pesan) =====
def generate_daily_schedule():
    """Generate jadwal dengan:
    - 2x fixed time (03:00 & 15:00 UTC)
    - 3x random time (16:00-20:00 UTC, menit 0/30)
    """
    schedule = {
        "03:00": Config.RESELLER_MESSAGE,  # 10:00 WIB
        "15:00": Config.RESELLER_MESSAGE   # 22:00 WIB
    }

    # Tambahkan 3 tweet acak (boleh duplikasi pesan)
    for _ in range(3):
        hour = random.randint(16, 20)
        minute = random.choice([0, 30])
        schedule[f"{hour:02d}:{minute:02d}"] = random.choice(Config.OTHER_MESSAGES)
    
    return schedule

# ===== Posting Tweet dengan Retry =====
def post_tweet(client, message):
    for attempt in range(Config.MAX_RETRIES + 1):
        try:
            response = client.create_tweet(text=message)
            logger.info(f"✅ Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
            return True
        except tweepy.TweepyException as e:
            if attempt < Config.MAX_RETRIES:
                logger.warning(f"⚠️ Coba lagi ({attempt + 1}/{Config.MAX_RETRIES})...")
                time.sleep(5)
            else:
                logger.error(f"❌ Gagal posting setelah {Config.MAX_RETRIES} percobaan: {e}")
    return False

# ===== Fungsi Utama =====
def main():
    logger.info("\n=== BOT DIMULAI ===")
    client = initialize_twitter_client()
    schedule = generate_daily_schedule()

    # Log jadwal
    logger.info("📅 Jadwal Hari Ini:")
    for time, msg in sorted(schedule.items()):
        logger.info(f"- {time} UTC: {msg[:50]}...")  # Tampilkan 50 karakter pertama

    # Cek waktu dengan toleransi
    current_time = datetime.datetime.utcnow()
    current_str = current_time.strftime("%H:%M")
    logger.info(f"🕒 Waktu Sekarang (UTC): {current_str}")

    posted = False
    for scheduled_time, message in schedule.items():
        scheduled = datetime.datetime.strptime(scheduled_time, "%H:%M")
        delta = abs((current_time - scheduled).total_seconds()) / 60  # Dalam menit

        if delta <= Config.TOLERANCE_MINUTES:
            logger.info(f"🎯 Menemukan jadwal: {scheduled_time} UTC (±{Config.TOLERANCE_MINUTES} menit)")
            if post_tweet(client, message):
                posted = True
                break  # Hanya post 1 tweet per eksekusi

    if not posted:
        logger.info("⏳ Tidak ada jadwal yang cocok")
    logger.info("=== BOT SELESAI ===\n")

if __name__ == "__main__":
    main()
