import tweepy
import os
import datetime

# ===== KONFIGURASI =====
print("\n=== BOT TWITTER DIMULAI ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# 1. Autentikasi Twitter
try:
    auth = tweepy.OAuth1UserHandler(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    api = tweepy.API(auth)
    user = api.verify_credentials()
    print(f"🔑 Terhubung ke Twitter sebagai @{user.screen_name.lstrip('0')}")
except Exception as e:
    print(f"❌ Gagal koneksi: {e}")
    exit()

# ===== JADWAL TWEET (UTC) =====
TWEET_SCHEDULE = {
    # WIB 00:00-00:20 (UTC 17:00-17:20)
    "17:00": "1. OPEN RESELLER! 🌟 Buka 07.00-03.00 WIB",
    # WIB 00:30-00:50 (UTC 17:30-17:50)
    "17:30": "5. Bismillah 🤲 Sehat & rezeki melimpah ✨",
    # WIB 01:00-01:20 (UTC 18:00-18:20)
    "18:00": "2. OPEN RESELLER! 🚀 Free konsultasi",
    # WIB 02:30-02:50 (UTC 19:30-19:50)
    "19:30": "3. Aku open ress",
    # WIB 03:00-03:20 (UTC 20:00-20:20)  # POSTINGAN BARU
    "20:00": "off dulss gaiss",
    # WIB 23:30-23:50 (UTC 16:30-16:50)
    "16:30": "4. Aku onn"
}

# ===== POSTING TWEET =====
current_time = datetime.datetime.utcnow()
current_hour = current_time.hour
current_min = current_time.minute
posted = False

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Rentang toleransi 15 menit sebelum - 20 menit setelah
    if (
        current_hour == schedule_hour
        and (schedule_min - 15) <= current_min <= (schedule_min + 20)
    ):
        try:
            api.update_status(message)
            print(f"✅ Tweet terkirim: '{message}'")
            posted = True
            break
        except Exception as e:
            print(f"❌ Gagal posting: {e}")

if not posted:
    print(f"⏳ Tidak ada jadwal (UTC: {current_time.strftime('%H:%M')}")

# ===== TESTING =====
# api.update_status("🤖 TEST: Bot aktif! " + datetime.datetime.now().strftime("%H:%M"))
