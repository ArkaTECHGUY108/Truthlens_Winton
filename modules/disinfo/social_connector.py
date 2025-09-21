# modules/disinfo/socialconnector.py

import aiohttp
from datetime import datetime
from core.config import settings

# ==============================
# Twitter / X Connector
# ==============================
async def fetch_twitter_mentions(query: str, limit: int = 10):
    """
    Fetch recent tweets about the claim.
    """
    if not settings.twitter_bearer:
        return [{
            "platform": "Twitter",
            "user": "@demo",
            "text": f"Mock tweet about {query}",
            "url": "",
            "timestamp": datetime.utcnow().isoformat()
        }]

    url = (
        f"https://api.twitter.com/2/tweets/search/recent"
        f"?query={query}&max_results={limit}&tweet.fields=created_at,author_id"
    )
    headers = {"Authorization": f"Bearer {settings.twitter_bearer}"}
    results = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                data = await resp.json()
                for t in data.get("data", []):
                    results.append({
                        "platform": "Twitter",
                        "user": t["author_id"],
                        "text": t["text"],
                        "url": f"https://twitter.com/i/web/status/{t['id']}",
                        "timestamp": t["created_at"]
                    })
        except Exception as e:
            print(f"[Twitter API Error] {e}")

    return results


# ==============================
# YouTube Connector
# ==============================
async def fetch_youtube_mentions(query: str, limit: int = 5):
    """
    Fetch YouTube video mentions about the claim.
    """
    if not settings.youtube_api_key:
        return [{
            "platform": "YouTube",
            "user": "demo_channel",
            "text": f"Mock YouTube video about {query}",
            "url": "",
            "timestamp": datetime.utcnow().isoformat()
        }]

    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={query}&maxResults={limit}&key={settings.youtube_api_key}"
    )
    results = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
                for item in data.get("items", []):
                    results.append({
                        "platform": "YouTube",
                        "user": item["snippet"]["channelTitle"],
                        "text": item["snippet"]["title"],
                        "url": f"https://www.youtube.com/watch?v={item['id'].get('videoId', '')}",
                        "timestamp": item["snippet"].get("publishTime", datetime.utcnow().isoformat())
                    })
        except Exception as e:
            print(f"[YouTube API Error] {e}")

    return results


# ==============================
# Facebook Connector
# ==============================
async def fetch_facebook_mentions(query: str, limit: int = 5):
    """
    Fetch Facebook page mentions about the claim.
    """
    if not settings.facebook_token:
        return [{
            "platform": "Facebook",
            "user": "demo_page",
            "text": f"Mock FB post about {query}",
            "url": "",
            "timestamp": datetime.utcnow().isoformat()
        }]

    url = (
        f"https://graph.facebook.com/v17.0/search"
        f"?q={query}&type=page&limit={limit}&access_token={settings.facebook_token}"
    )
    results = []

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
                for item in data.get("data", []):
                    results.append({
                        "platform": "Facebook",
                        "user": item.get("name", "unknown"),
                        "text": f"Page mentioning {query}",
                        "url": f"https://facebook.com/{item.get('id')}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            print(f"[Facebook API Error] {e}")

    return results


# ==============================
# Unified Aggregator
# ==============================
async def fetch_social_signals(query: str, limit: int = 5):
    """
    Aggregates claims across Twitter, YouTube, and Facebook.
    Always returns a list of normalized dicts.
    """
    results = []
    results.extend(await fetch_twitter_mentions(query, limit))
    results.extend(await fetch_youtube_mentions(query, limit))
    results.extend(await fetch_facebook_mentions(query, limit))
    return results