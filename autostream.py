import os
import datetime
import random
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# আজকের তারিখ দিয়ে সুন্দর টাইটেল
TODAY_STR = datetime.datetime.utcnow().strftime("%d %B, %Y")
STREAM_TITLE = f"Daily Puzzle Challenge - {TODAY_STR}"
STREAM_DESC = "Enjoy our daily scheduled live stream! #Puzzle #Live"

def main():
    print("🚀 Initializing YouTube API...")
    
    # সিক্রেট থেকে তথ্য নিচ্ছে
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise ValueError("❌ Secrets Missing! Check Github Settings.")

    # ১. ইউটিউবে লগইন (Server Side)
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    youtube = build("youtube", "v3", credentials=creds)

    print(f"creating Broadcast: {STREAM_TITLE}")

    # ২. নতুন ব্রডকাস্ট তৈরি (Auto Start & Stop ON)
    broadcast_body = {
        "snippet": {
            "title": STREAM_TITLE,
            "description": STREAM_DESC,
            "scheduledStartTime": (datetime.datetime.utcnow() + datetime.timedelta(seconds=30)).isoformat() + "Z"
        },
        "status": {
            "privacyStatus": "public",
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

    # ৩. স্ট্রিম কী (Stream Key) জেনারেট করা
    stream_body = {
        "snippet": { "title": "GitHub Auto Key" },
        "cdn": { "format": "1080p", "ingestionType": "rtmp" }
    }
    stream_response = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=stream_body
    ).execute()
    
    stream_id = stream_response["id"]
    ingestion_info = stream_response["cdn"]["ingestionInfo"]
    rtmp_url = ingestion_info["ingestionAddress"]
    stream_key = ingestion_info["streamName"]
    
    print(f"✅ Stream Key Generated!")

    # ৪. ব্রডকাস্ট এবং কী-এর মধ্যে সংযোগ (Bind)
    youtube.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast_id,
        streamId=stream_id
    ).execute()
    
    print("✅ Bind Successful! Ready to Stream.")

    # ৫. GitHub Actions-এ তথ্য পাঠানো (পরের ধাপে FFmpeg ব্যবহারের জন্য)
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f"server_url={rtmp_url}", file=f)
        print(f"stream_key={stream_key}", file=f)

if __name__ == "__main__":
    main()