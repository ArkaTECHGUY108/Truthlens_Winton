import aiohttp
from core.config import settings
from core.logger import setup_logger

logger = setup_logger()

NEWS_API_URL = "https://newsapi.org/v2/everything"

async def fetch_news_articles(query: str, limit: int = 3):
    """
    Fetch recent news articles about the claim using NewsAPI.
    """
    if not settings.newsapi_key:
        logger.warning("NEWSAPI_KEY not configured.")
        return []

    params = {
        "q": query,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": limit,
        "apiKey": settings.newsapi_key,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(NEWS_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"NewsAPI error {resp.status}")
                    return []
                data = await resp.json()
                return data.get("articles", [])
    except Exception as e:
        logger.error(f"[NewsAPI Fetch Error] {e}")
        return []
