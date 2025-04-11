import tweepy
import os
import datetime
import json
import time
import random

# ===== KONFIGURASI =====
print("\n=== BOT TWITTER DIMULAI ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))

# 1. Autentikasi
def initialize_twitter_client():
    try:
        client = tweepy.Client(
            consumer_key=os.environ["API_KEY"],
            consumer_secret=os.environ["API_SECRET"],
            access_token=os.environ["ACCESS_TOKEN"],
            access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
        )
        user = client.get_me()
        print(f"🔑 Terhubung ke Twitter sebagai @{user.data.username}")
        return client
    except Exception as e:
        print(f"❌ Gagal koneksi: {e}")
        exit()

client = initialize_twitter_client()

# ===== FUNGSI ANTI DUPLIKASI =====
def save_last_post(time_key):
    try:
        with open('last_post.json', 'w') as f:
            json.dump({"last_post": time_key, "timestamp": datetime.datetime.utcnow().isoformat()}, f)
    except Exception as e:
        print(f"❌ Gagal menyimpan last_post: {e}")

def load_last_post():
    try:
        with open('last_post.json', 'r') as f:
            data = json.load(f)
            # Cek jika post terakhir lebih dari 12 jam yang lalu
            post_time = datetime.datetime.fromisoformat(data["timestamp"])
            if (datetime.datetime.utcnow() - post_time).total_seconds() >= 12 * 3600:
                return None
            return data.get("last_post")
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None
    except Exception as e:
        print(f"❌ Error load_last_post: {e}")
        return None

# ===== JADWAL TWEET =====
RESELLER_MESSAGE = "OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun yaa"

OTHER_MESSAGES = [
    "Aku onn",
    "Bismillah 🤲 Sehat & rezeki melimpah ✨",
    "Aku open ress",
    "off dulss gaiss",
    "Jangan lupa follow @xiaojdun untuk update terbaru!",
    "Pagi semangat! Jangan lupa minum air putih 💧"
]

# Generate schedule
def generate_schedule():
    # 2x RESELLER_MESSAGE (12 hours apart)
    reseller_times = [
        ("15:00", RESELLER_MESSAGE),  # 22:00 WIB
        ("03:00", RESELLER_MESSAGE)    # 10:00 WIB
    ]
    
    # 3 posts between 16:00-20:00 UTC (23:00-03:00 WIB)
    night_posts = []
    night_hours = [16, 17, 18, 19, 20]  # UTC hours
    for _ in range(3):
        hour = random.choice(night_hours)
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        night_posts.append((time_str, random.choice(OTHER_MESSAGES)))
    
    # 3 random posts during other times
    other_posts = []
    for _ in range(3):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        # Avoid times too close to scheduled posts
        while hour in [3, 15] or (16 <= hour <= 20):
            hour = random.randint(0, 23)
        time_str = f"{hour:02d}:{minute:02d}"
        other_posts.append((time_str, random.choice(OTHER_MESSAGES)))
    
    # Combine all schedules
    schedule = {}
    for time_str, msg in reseller_times + night_posts + other_posts:
        schedule[time_str] = msg
    
    return schedule

TWEET_SCHEDULE = generate_schedule()
print("📅 Jadwal Tweet Hari Ini:")
for time_str, msg in sorted(TWEET_SCHEDULE.items()):
    print(f"{time_str} UTC: {msg[:30]}...")

# ===== POSTING TWEET =====
def post_tweet(message):
    try:
        response = client.create_tweet(text=message)
        print(f"✅ Tweet terkirim: https://twitter.com/user/status/{response.data['id']}")
        return True
    except tweepy.TweepyException as e:
        print(f"❌ Gagal posting (Tweepy): {e}")
    except Exception as e:
        print(f"❌ Gagal posting (Umum): {e}")
    return False

def check_schedule():
    current_time = datetime.datetime.utcnow()
    current_hour_min = current_time.strftime("%H:%M")
    print(f"\n🕒 Memeriksa jadwal (UTC: {current_hour_min})")

    last_post = load_last_post()
    posted = False

    for schedule_time, message in TWEET_SCHEDULE.items():
        schedule_hour, schedule_min = map(int, schedule_time.split(":"))
        
        # Cek waktu dengan toleransi 15 menit sebelum - 20 menit setelah
        if (current_time.hour == schedule_hour and 
            (schedule_min - 15) <= current_time.minute <= (schedule_min + 20)):
            
            if last_post != schedule_time:
                if post_tweet(message):
                    save_last_post(schedule_time)
                    posted = True
                    time.sleep(60)  # Tunggu 1 menit setelah posting
                break  # Hanya proses satu tweet per eksekusi

    if not posted:
        print(f"⏳ Tidak ada jadwal yang cocok (UTC: {current_hour_min})")

# ===== MAIN LOOP =====
if __name__ == "__main__":
    # Generate new schedule daily
    last_schedule_day = datetime.datetime.utcnow().day
    
    while True:
        try:
            # Generate new schedule at midnight UTC
            current_day = datetime.datetime.utcnow().day
            if current_day != last_schedule_day:
                TWEET_SCHEDULE = generate_schedule()
                last_schedule_day = current_day
                print("\n🔄 Membuat jadwal baru untuk hari ini:")
                for time_str, msg in sorted(TWEET_SCHEDULE.items()):
                    print(f"{time_str} UTC: {msg[:30]}...")
            
            check_schedule()
            time.sleep(300)  # Cek setiap 5 menit
            
        except KeyboardInterrupt:
            print("\n🛑 Bot dihentikan manual")
            break
        except Exception as e:
            print(f"❌ Error dalam main loop: {e}")
            time.sleep(60)
