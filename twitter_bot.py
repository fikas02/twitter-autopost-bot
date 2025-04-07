import tweepy
import os
import datetime

# ===== 1. CONFIGURATION =====
print("\n=== TWITTER BOT STARTED ===")
print("UTC Time:", datetime.datetime.utcnow().strftime("%H:%M"))
print("Timezone:", datetime.datetime.utcnow().astimezone().tzinfo)  # Added timezone info

# Twitter Authentication
try:
    auth = tweepy.OAuth1UserHandler(
        consumer_key=os.environ["API_KEY"],
        consumer_secret=os.environ["API_SECRET"],
        access_token=os.environ["ACCESS_TOKEN"],
        access_token_secret=os.environ["ACCESS_TOKEN_SECRET"]
    )
    api = tweepy.API(auth)
    
    # Verify Connection
    user = api.verify_credentials()
    print(f"🔑 Connected to Twitter as @{user.screen_name.strip('@')}")  # Fixed username format
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit()

# ===== TWEET SCHEDULE =====
TWEET_SCHEDULE = {
    # UTC Time : Message
    "17:00": "1. OPEN RESELLER! 🌟 Buka 07.00-03.00 WIB",
    "17:30": "5. Bismillah 🤲 Sehat & rezeki melimpah ✨",
    "18:00": "2. OPEN RESELLER! 🚀 Free konsultasi",
    "19:30": "3. aku open ress",
    "16:30": "4. aku onn"
}

# ===== 3. AUTO POSTING WITH ENHANCED LOGGING =====
current_utc = datetime.datetime.utcnow().strftime("%H:%M")
next_scheduled = min(TWEET_SCHEDULE.keys())  # Added next schedule info
print(f"Next scheduled tweet at UTC: {next_scheduled}")

if current_utc in TWEET_SCHEDULE:
    try:
        tweet = api.update_status(TWEET_SCHEDULE[current_utc])
        print(f"✅ Tweeted: https://twitter.com/user/status/{tweet.id}")
    except tweepy.TweepyException as e:
        print(f"❌ Failed to tweet: {e}")
else:
    print(f"⏳ No scheduled tweet (UTC: {current_utc})")

# ===== TESTING =====
# Uncomment below to test immediately
# api.update_status("🤖 TEST: Bot is working! " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
