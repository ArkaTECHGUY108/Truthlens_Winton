import aiohttp
from core.logger import setup_logger

logger = setup_logger()

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

async def fetch_wikipedia_snippets(query: str, limit: int = 2):
    """
    Fetch Wikipedia search snippets for background evidence.
    Always sets a User-Agent header to avoid 403 errors.
    """
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "utf8": 1,
        "format": "json",
        "srlimit": limit,
    }

    headers = {"User-Agent": "TruthLensBot/1.0 (contact: research@iem.ac.in)"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(WIKI_API_URL, params=params, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"Wikipedia API error {resp.status}")
                    return []
                data = await resp.json()
                results = []
                for item in data.get("query", {}).get("search", []):
                    results.append({
                        "snippet": item.get("snippet", "")
                                    .replace("<span class=\"searchmatch\">", "")
                                    .replace("</span>", ""),
                        "url": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                    })
                return results
    except Exception as e:
        logger.error(f"[Wikipedia Fetch Error] {e}")
        return []
