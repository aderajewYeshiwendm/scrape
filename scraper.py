import tweepy
import yaml
import json
import time
import os
from utils import save_to_csv
import pandas as pd

# Load config
with open("config.yaml") as f:
    config = yaml.safe_load(f)

client = tweepy.Client(
    bearer_token=config['twitter']['bearer_token'],
    consumer_key=config['twitter']['api_key'],
    consumer_secret=config['twitter']['api_secret'],
    wait_on_rate_limit=True
)

def get_user_id(handle: str) -> str:
    """Cache user ID to avoid lookup every run"""
    cache_file = f".cache_{handle}.json"
    if os.path.exists(cache_file):
        return json.load(open(cache_file))["user_id"]

    user = client.get_user(username=handle, user_fields=["id"])
    user_id = str(user.data.id)
    json.dump({"user_id": user_id}, open(cache_file, "w"))
    return user_id

def scrape_followers(handle: str):
    user_id = get_user_id(handle)
    print(f"Scraping followers of @{handle} (ID: {user_id})")

    paginator = tweepy.Paginator(
        client.get_users_followers,
        id=user_id,
        max_results=1000,
        user_fields=[
            "name", "username", "description", "location",
            "verified", "public_metrics", "created_at",
            "profile_image_url"
        ]
    )

    followers = []
    seen = set()

    for response in paginator:
        if not response.data:
            break

        for user in response.data:
            uid = user.id
            if uid in seen:
                continue
            seen.add(uid)

            metrics = user.public_metrics
            followers.append({
                "user_id": uid,
                "handle": user.username,
                "name": user.name,
                "description": user.description or "",
                "location": user.location or "",
                "verified": user.verified,
                "followers_count": metrics['followers_count'],
                "following_count": metrics['following_count'],
                "tweet_count": metrics['tweet_count'],
                "created_at": user.created_at.isoformat() if user.created_at else "",
                "profile_image_url": user.profile_image_url or ""
            })

        print(f"Fetched {len(followers):,} so far...")

        # Respect rate limits automatically (wait_on_rate_limit=True)

    df = pd.DataFrame(followers)
    path = save_to_csv(df, handle, config['output']['folder'])
    return path

if __name__ == "__main__":
    for acc in config['accounts']:
        scrape_followers(acc['handle'])