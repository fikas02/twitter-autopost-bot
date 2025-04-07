import tweepy
import os
import datetime

# Twitter API Config
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# Authentication
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Tweet Contents
tweet_contents = [
    "1. OPEN RESELLER! 🌟\nFH buka 07.00 - 03.00, 3 admin, aplikasi 70+, garansi mostly 0-1d! No fee, no target! Cek PL dulu! 💬 Tanyakan langsung ke @xiaojdun di Twitter atau WA di bio! #OpenReseller #BisnisOnline #Aplikasi",
    "2. OPEN RESELLER! Halo, kak! FH saya open dari 07.00 - 03.00 subuh, ada 3 admin fsr, aplikasi 70+ dan garansi mostly 0-1d! bisa kepoin pl nya dulu🤍feel free to ask buat ress baru! last, no fee no target! bisa tanya\" ke twt @xiaojdun atau untuk fsr ke WA di bio @xiaojdun ya",
    "3. akuu open ress loh kakk",
    "4. aku onn",
    "5. Bismillah 🤲\n\nSemoga kita semua:\n• Sehat selalu 💊\n• Bahagia dunia akhirat 🌈\n• Rezeki melimpah ruah 💰\n\nAamiin ya Rabbal'alamin ✨"
]

# Post Tweet Function
def post_tweet(message):
    try:
        api.update_status(message)
        print(f"✅ Tweeted: {message}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Schedule Check
current_time = datetime.datetime.now().strftime("%H:%M")

if current_time == "17:00":    # 00:00 WIB
    post_tweet(tweet_contents[0])
elif current_time == "17:30":  # 00:30 WIB (NEW)
    post_tweet(tweet_contents[4])
elif current_time == "18:00":  # 01:00 WIB
    post_tweet(tweet_contents[1])
elif current_time == "19:30":  # 02:30 WIB
    post_tweet(tweet_contents[2])
elif current_time == "16:30":  # 23:30 WIB
    post_tweet(tweet_contents[3])
else:
    print(f"🕒 Sekarang jam {current_time} UTC, belum waktunya posting.")
