import asyncpraw
from core.config import settings
from core.logger import setup_logger

logger = setup_logger()

# Async Reddit client
reddit = asyncpraw.Reddit(
    client_id=settings.reddit_client_id,
    client_secret=settings.reddit_client_secret,
    user_agent=settings.reddit_user_agent,
)

async def fetch_reddit_mentions(query: str, limit: int = 5):
    """
    Search Reddit for recent mentions of the claim.
    """
    results = []
    try:
        subreddit = await reddit.subreddit("all", fetch=True)
        async for submission in subreddit.search(query, limit=limit):
            results.append({
                "title": submission.title,
                "text": submission.selftext,
                "subreddit": submission.subreddit.display_name,
                "created_utc": submission.created_utc
            })
    except Exception as e:
        logger.error(f"[Reddit API Error] {e}")
        return []
    return results
