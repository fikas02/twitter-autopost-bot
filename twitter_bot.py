import tweepy
import os
import datetime

# ===== KONFIGURASI =====
print("\n=== BOT TWITTER DIMULAI ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# 1. Autentikasi dengan Twitter API V2
try:
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    # Verifikasi koneksi
    user = client.get_me()
    print(f"🔑 Terhubung ke Twitter sebagai @{user.data.username}")
except Exception as e:
    print(f"❌ Gagal koneksi: {e}")
    exit()

# ===== JADWAL TWEET (UTC) =====
TWEET_SCHEDULE = {
    "17:00": "1. OPEN RESELLER! 🌟 Buka 07.00-03.00 WIB",  # 00:00 WIB
    "17:30": "5. Bismillah 🤲 Sehat & rezeki melimpah ✨",  # 00:30 WIB
    "18:00": "2. OPEN RESELLER! 🚀 Free konsultasi",       # 01:00 WIB
    "19:30": "3. Aku open ress",                          # 02:30 WIB
    "20:00": "off dulss gaiss",                           # 03:00 WIB (POSTINGAN BARU)
    "16:30": "4. Aku onn"                                 # 23:30 WIB
}

# ===== POSTING TWEET =====
current_time = datetime.datetime.utcnow()
posted = False

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Rentang toleransi 15 menit sebelum - 20 menit setelah
    if (
        current_time.hour == schedule_hour
        and (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)
    ):
        try:
            response = client.create_tweet(text=message)
            print(f"✅ Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
            posted = True
        except Exception as e:
            print(f"❌ Gagal posting: {e}")

if not posted:
    print(f"⏳ Tidak ada jadwal (UTC: {current_time.strftime('%H:%M')})")

# ===== TESTING =====
# Uncomment untuk test langsung:
# client.create_tweet(text="🤖 TEST: Bot aktif! " + datetime.datetime.now().strftime("%H:%M"))
