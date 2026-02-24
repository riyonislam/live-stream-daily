import os
import datetime
import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- কনফিগারেশন (আপনার দেওয়া তথ্য) ---
# টাইটেল (সাথে তারিখ যোগ করা হলো যাতে ডুপ্লিকেট না দেখায়)
TODAY = datetime.datetime.now().strftime("%d %B %Y")
STREAM_TITLE = f"Daily Mind Game Challenge | LIVE Puzzle Challenge | {TODAY}"

STREAM_DESCRIPTION = """Welcome to the Daily Live Puzzle Challenge! 🧠⚡

Test your brain power with exciting puzzles and mind games — and remember, you only get 60 seconds to solve each one!

🔥 Play along in real time  
⏱️ One minute per puzzle  
🏆 Challenge your IQ  
💬 Compete with other viewers in the chat  

Whether you love riddles, brain teasers, logic puzzles, or tricky challenges, this live stream is designed to sharpen your mind and boost your thinking speed.

👉 Don’t forget to LIKE 👍  
👉 SUBSCRIBE for daily puzzle lives  
👉 Turn on the notification bell 🔔 so you never miss a challenge!

Are you ready to prove you're a puzzle master? Let’s begin!"""

# ট্যাগস লিস্ট
STREAM_TAGS = [
    "live puzzle", "puzzle live", "brain teaser live", "iq test live", "mind games live",
    "puzzle challenge", "brain challenge", "riddles live", "logic puzzles", "test your iq",
    "genius puzzle", "daily puzzle", "interactive live", "youtube live games",
    "thinking games", "smart games", "brain workout", "puzzle stream",
    "live brain teaser", "60 second challenge", "quick puzzles", "viral puzzles", "fun puzzles"
]

def main():
    print("🚀 Initializing YouTube API...")

    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise ValueError("❌ Secrets Missing! Check Github Settings.")

    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    youtube = build("youtube", "v3", credentials=creds)

    print(f"Creating Broadcast: {STREAM_TITLE}")

    # ১. ব্রডকাস্ট তৈরি (Title, Desc, Tags সহ)
    broadcast_body = {
        "snippet": {
            "title": STREAM_TITLE,
            "description": STREAM_DESCRIPTION,
            "tags": STREAM_TAGS,  # ট্যাগস এখানে বসানো হলো
            "scheduledStartTime": (datetime.datetime.utcnow() + datetime.timedelta(seconds=30)).isoformat() + "Z"
        },
        "status": {
            "privacyStatus": "public",  # সরাসরি পাবলিক হবে
            "selfDeclaredMadeForKids": False
        },
        "contentDetails": {
            "enableAutoStart": True, 
            "enableAutoStop": True,
            "monitorStream": { "enableMonitorStream": False }
        }
    }

    broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body=broadcast_body
    ).execute()

    broadcast_id = broadcast_response["id"]
    print(f"✅ Broadcast Created! ID: {broadcast_id}")

    # ২. স্ট্রিম কী (Stream Key) তৈরি - [FIXED FOR VERTICAL VIDEO]
    # 'variable' রেজোলিউশন দিলে ইউটিউব ৯:১৬ রেশিও সাপোর্ট করবে এবং 'Resolution required' এরর আসবে না।
    stream_body = {
        "snippet": { "title": "Vertical Auto Key" },
        "cdn": {
            "ingestionType": "rtmp",
            "resolution": "variable", 
            "frameRate": "variable"
        }
    }

    stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=stream_body
    ).execute()

    stream_id = stream_response["id"]
    ingestion_info = stream_response["cdn"]["ingestionInfo"]
    rtmp_url = ingestion_info["ingestionAddress"]
    stream_key = ingestion_info["streamName"]

    print(f"✅ Stream Key Generated: {stream_key[:5]}...")

    # ৩. ব্রডকাস্ট এবং স্ট্রিম কি বাইন্ড (Bind)
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()

    print("✅ Bind Successful!")

    # ৪. আউটপুট পাঠানো (গিটহাবের জন্য)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f"server_url={rtmp_url}", file=f)
        print(f"stream_key={stream_key}", file=f)

if __name__ == "__main__":
    main()
