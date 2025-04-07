import tweepy
import os
import datetime

# Debug info
print("=== BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# Twitter API Setup
auth = tweepy.OAuth1UserHandler(
    consumer_key=os.environ.get("API_KEY"),
    consumer_secret=os.environ.get("API_SECRET"),
    access_token=os.environ.get("ACCESS_TOKEN"),
    access_token_secret=os.environ.get("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# Tweet Contents
SCHEDULED_TWEETS = {
    "17:00": "1. OPEN RESELLER! 🌟 Buka 07.00-03.00 WIB",  # 00:00 WIB
    "17:30": "5. Bismillah 🤲 Sehat & rezeki melimpah ✨",  # 00:30 WIB
    "18:00": "2. OPEN RESELLER! 🚀 Free konsultasi",       # 01:00 WIB
    "19:30": "3. aku open ress",                          # 02:30 WIB
    "16:30": "4. aku onn"                                 # 23:30 WIB
}

# Post Tweet
current_time_utc = datetime.datetime.utcnow().strftime("%H:%M")
if current_time_utc in SCHEDULED_TWEETS:
    try:
        tweet = api.update_status(SCHEDULED_TWEETS[current_time_utc])
        print(f"✅ POSTED: {tweet.id}")
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
else:
    print(f"⏳ Not scheduled (UTC: {current_time_utc})")

# Uncomment to test immediately
# api.update_status("🔧 TEST: Bot is working!")
