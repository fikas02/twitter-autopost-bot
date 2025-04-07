import tweepy
import os
import datetime
import time

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
    "1. OPEN RESELLER! 🌟 FH buka 07.00-03.00...",  # 00:00 WIB
    "2. OPEN RESELLER! Halo kak...",                # 01:00 WIB 
    "3. akuu open ress loh kakk",                   # 02:30 WIB
    "4. aku onn",                                   # 23:30 WIB
    "5. Bismillah 🤲 Sehat selalu 💊 Bahagia 🌈 Rezeki melimpah 💰 Aamiin ✨"  # 00:30 WIB
]

# Posting Function
def post_tweet(msg):
    try:
        api.update_status(msg)
        print(f"✅ Tweeted: {msg}")
    except Exception as e:
        print(f"❌ Failed: {e}")

# Main Logic
current_time = datetime.datetime.now().strftime("%H:%M")

if current_time == "17:00":    post_tweet(tweets[0])  # 00:00 WIB
elif current_time == "17:30":  post_tweet(tweets[4])  # 00:30 WIB
elif current_time == "18:00":  post_tweet(tweets[1])  # 01:00 WIB 
elif current_time == "19:30":  post_tweet(tweets[2])  # 02:30 WIB
elif current_time == "16:30":  post_tweet(tweets[3])  # 23:30 WIB
else:
    print(f"⏳ Not time yet (UTC: {current_time})")
    time.sleep(60)  # Wait 1 minute if not time
