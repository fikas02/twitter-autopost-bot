import tweepy
import os
import datetime

# Debugging header
print("=== BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))

# Twitter API Config
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# Verify credentials
try:
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    user = api.verify_credentials()
    print(f"🔑 Connected to Twitter as @{user.screen_name}")
except Exception as e:
    print(f"❌ Twitter connection failed: {e}")
    exit()

# Tweet Contents
tweets = [
    "1. OPEN RESELLER! 🌟",  # 00:00 WIB
    "2. OPEN RESELLER! 🚀",  # 01:00 WIB
    "3. aku open ress",      # 02:30 WIB
    "4. aku onn",           # 23:30 WIB
    "5. Bismillah 🤲\n\nKita semua sehat 💊\nBahagia 🌈\nRezeki melimpah 💰\nAamiin ✨"  # 00:30 WIB
]

# Posting function
def tweet_now(message):
    try:
        tweet = api.update_status(message)
        print(f"✅ TWEETED: https://twitter.com/user/status/{tweet.id}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__} - {e}")
        return False

# Schedule check (UTC)
current_time = datetime.datetime.utcnow()
current_hour = current_time.hour
current_min = current_time.minute

# Wide time windows (WIB = UTC+7)
if current_hour == 17 and 0 <= current_min < 15:    # 00:00-00:15 WIB
    tweet_now(tweets[0])
    
elif current_hour == 17 and 25 <= current_min < 40:  # 00:25-00:40 WIB
    tweet_now(tweets[4])
    
elif current_hour == 18 and 0 <= current_min < 15:   # 01:00-01:15 WIB
    tweet_now(tweets[1])
    
elif current_hour == 19 and 25 <= current_min < 40:  # 02:25-02:40 WIB
    tweet_now(tweets[2])
    
elif current_hour == 16 and 25 <= current_min < 40:  # 23:25-23:40 WIB
    tweet_now(tweets[3])
    
else:
    print(f"⏰ Not scheduled (UTC {current_hour}:{current_min})")

# TEST MODE (Uncomment to force tweet)
# tweet_now("🔧 TEST: Bot is working! " + str(datetime.datetime.now()))
