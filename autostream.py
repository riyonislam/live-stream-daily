import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TODAY_STR = datetime.datetime.utcnow().strftime("%d %B, %Y")
STREAM_TITLE = f"Daily Puzzle Challenge - {TODAY_STR}"
STREAM_DESC = "Enjoy our daily scheduled live stream! #Puzzle #Live"

def main():
    print("🚀 Initializing YouTube API...")
    
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN")

    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise ValueError("❌ Secrets Missing!")

    creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri="https://oauth2.googleapis.com/token", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    youtube = build("youtube", "v3", credentials=creds)

    print(f"Creating Broadcast: {STREAM_TITLE}")

    # ১. ব্রডকাস্ট তৈরি
    broadcast_body = {
        "snippet": {
            "title": STREAM_TITLE,
            "description": STREAM_DESC,
            "scheduledStartTime": (datetime.datetime.utcnow() + datetime.timedelta(seconds=60)).isoformat() + "Z"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        },
        "contentDetails": {
            "enableAutoStart": True,
            "enableAutoStop": True
        }
    }
    
    broadcast_resp = youtube.liveBroadcasts().insert(part="snippet,status,contentDetails", body=broadcast_body).execute()
    broadcast_id = broadcast_resp["id"]
    print(f"✅ Broadcast Created! ID: {broadcast_id}")

    # ২. স্ট্রিম কী (Stream Key) তৈরি - [UPDATED FIX]
    stream_body = {
        "snippet": { "title": "GitHub Auto Key" },
        "cdn": {
            "format": "",           # এটি খালি রাখা বা না দেওয়াই ভালো variable এর জন্য
            "ingestionType": "rtmp",
            "resolution": "variable", 
            "frameRate": "variable" 
        }
    }
    
    # কিছু অ্যাকাউন্টে resolution ফিল্ড বাধ্যতামূলক থাকে না যদি 'variable' দেওয়া হয়
    # তাই আমরা আরও নিরাপদ পদ্ধতি ব্যবহার করছি:
    
    stream_insert = youtube.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": { "title": "Auto Stream Key" },
            "cdn": {
                "ingestionType": "rtmp",
                "resolution": "variable",  # ফিক্সড সাইজ না দিয়ে ভেরিয়েবল দেওয়া হলো
                "frameRate": "variable"
            }
        }
    )
    stream_resp = stream_insert.execute()
    
    stream_id = stream_resp["id"]
    ingestion = stream_resp["cdn"]["ingestionInfo"]
    rtmp_url = ingestion["ingestionAddress"]
    stream_key = ingestion["streamName"]
    
    print(f"✅ Stream Key Generated!")

    # ৩. বাইন্ড
    youtube.liveBroadcasts().bind(part="id,contentDetails", id=broadcast_id, streamId=stream_id).execute()
    print("✅ Bind Successful!")

    # ৪. আউটপুট
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f"server_url={rtmp_url}", file=f)
        print(f"stream_key={stream_key}", file=f)

if __name__ == "__main__":
    main()
