import aiohttp
from core.config import settings
from core.logger import setup_logger

logger = setup_logger()

FACTCHECK_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

async def fetch_factcheck_articles(query: str, limit: int = 3):
    """
    Fetch fact-check articles from Google FactCheck Tools API.
    Normalizes response into list of dicts.
    """
    params = {
        "query": query,
        "key": settings.factcheck_api_key,
        "pageSize": limit,
        "languageCode": "en"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FACTCHECK_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"[FactCheck API] HTTP {resp.status}")
                    return []

                data = await resp.json()
                claims = data.get("claims", [])
                results = []

                for c in claims:
                    review = c.get("claimReview", [{}])[0]
                    results.append({
                        "text": c.get("text", ""),
                        "url": review.get("url", ""),
                        "publisher": review.get("publisher", {}).get("name", ""),
                        "date": review.get("reviewDate", "")
                    })
                return results
    except Exception as e:
        logger.error(f"[FactCheck API Error] {e}")
        return []
