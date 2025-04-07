import tweepy
import os
import datetime
import json

# ===== KONFIGURASI =====
print("\n=== BOT TWITTER DIMULAI ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# 1. Autentikasi
try:
    client = tweepy.Client(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    user = client.get_me()
    print(f"🔑 Terhubung ke Twitter sebagai @{user.data.username}")
except Exception as e:
    print(f"❌ Gagal koneksi: {e}")
    exit()

# ===== FUNGSI ANTI DUPLIKASI =====
def save_last_post(time_key):
    with open('last_post.json', 'w') as f:
        json.dump({"last_post": time_key}, f)

def load_last_post():
    try:
        with open('last_post.json', 'r') as f:
            return json.load(f).get("last_post")
    except:
        return None

# ===== JADWAL TWEET (UTC) =====
TWEET_SCHEDULE = {
    # Waktu UTC (WIB = UTC+7)
    "16:00": "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun yaa",  # 23:00 WIB
    "16:30": "4. Aku onn",                                                         # 23:30 WIB
    "17:00": "1. OPEN RESELLER! 🌟 Buka 07.00-03.00 WIB",                          # 00:00 WIB
    "17:30": "5. Bismillah 🤲 Sehat & rezeki melimpah ✨",                          # 00:30 WIB
    "18:00": "2. OPEN RESELLER! 🚀 Free konsultasi",                               # 01:00 WIB
    "19:30": "3. Aku open ress",                                                   # 02:30 WIB
    "20:00": "off dulss gaiss",                                                    # 03:00 WIB
    "21:00": "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun yaa"  # 04:00 WIB
}

# ===== POSTING TWEET =====
current_time = datetime.datetime.utcnow()
posted = False
last_post = load_last_post()

for schedule_time, message in TWEET_SCHEDULE.items():
    schedule_hour, schedule_min = map(int, schedule_time.split(":"))
    
    # Cek waktu dengan toleransi 15 menit sebelum - 20 menit setelah
    if (current_time.hour == schedule_hour and 
        (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)):
        
        # Cek apakah sudah pernah diposting
        if last_post != schedule_time:
            try:
                response = client.create_tweet(text=message)
                save_last_post(schedule_time)
                print(f"✅ Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
                posted = True
            except Exception as e:
                print(f"❌ Gagal posting: {e}")

if not posted:
    print(f"⏳ Tidak ada jadwal (UTC: {current_time.strftime('%H:%M')})")
