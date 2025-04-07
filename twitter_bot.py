import tweepy
import os
import datetime

# 1. Auth Setup
auth = tweepy.OAuth1UserHandler(
    os.environ.get("API_KEY"),
    os.environ.get("API_SECRET"),
    os.environ.get("ACCESS_TOKEN"),
    os.environ.get("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

# 2. Tweet Schedule (UTC Times)
TWEET_SCHEDULE = {
    "17:00": "🕛 00:00 WIB: Buka reseller!",
    "17:30": "🤲 Bismillah, semoga berkah",
    "18:00": "🕐 01:00 WIB: Promo khusus!",
    "19:30": "💼 Yuk join reseller kami",
    "16:30": "🌙 Selamat malam calon reseller!"
}

# 3. Execution
current_utc = datetime.datetime.utcnow().strftime("%H:%M")
if current_utc in TWEET_SCHEDULE:
    try:
        api.update_status(TWEET_SCHEDULE[current_utc])
        print(f"✅ Posted at {current_utc} UTC")
    except tweepy.TweepyException as e:
        print(f"❌ Twitter error: {e}")
else:
    print(f"⏱️ No post scheduled for {current_utc} UTC")

# Uncomment to test:
# api.update_status(f"🔧 Test tweet at {datetime.datetime.now()}")
