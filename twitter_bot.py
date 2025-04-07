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
tweets = [
    # 00:00 WIB
    "1. OPEN RESELLER! 🌟 FH buka 07.00-03.00, 3 admin, aplikasi 70+...",
    
    # 01:00 WIB
    "2. OPEN RESELLER! Halo kak! FH saya open dari 07.00-03.00 subuh...",
    
    # 02:30 WIB
    "3. akuu open ress loh kakk",
    
    # 23:30 WIB
    "4. aku onn",
    
    # 00:30 WIB (NEW)
    "5. Bismillah 🤲\n\nSemoga kita semua:\n• Sehat selalu 💊\n• Bahagia dunia akhirat 🌈\n• Rezeki melimpah 💰\n\nAamiin ✨"
]

def post_tweet(msg):
    try:
        api.update_status(msg)
        print(f"✅ Tweeted: {msg}")
        return True
    except Exception as e:
        print(f"❌ Failed to post: {e}")
        return False

# Main Logic
now = datetime.datetime.utcnow()
current_hour = now.hour
current_min = now.minute

# Wide time windows to prevent missing schedules
if current_hour == 17 and 0 <= current_min <= 10:    # 00:00-00:10 WIB
    post_tweet(tweets[0])
    
elif current_hour == 17 and 25 <= current_min <= 35:  # 00:25-00:35 WIB
    post_tweet(tweets[4])
    
elif current_hour == 18 and 0 <= current_min <= 10:   # 01:00-01:10 WIB
    post_tweet(tweets[1])
    
elif current_hour == 19 and 25 <= current_min <= 40:  # 02:25-02:40 WIB
    post_tweet(tweets[2])
    
elif current_hour == 16 and 25 <= current_min <= 35:  # 23:25-23:35 WIB
    post_tweet(tweets[3])
    
else:
    print(f"⏰ UTC Time: {current_hour}:{current_min} - Not scheduled")

# TESTING ONLY - Uncomment to force post now
# post_tweet("🔧 TEST: System check at " + str(datetime.datetime.now()))
