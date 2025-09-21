# backend/services/google_factcheck.py

import aiohttp
from core.config import settings

async def query_factcheck_api(query: str) -> list:
    """
    Queries Google Fact Check Tools API with the claim text.
    Returns a list of source URLs.
    """
    url = (
        f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
        f"?query={query}&key={settings.factcheck_api_key}"
    )

    sources = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if "claims" in data:
                    for claim in data["claims"]:
                        if "claimReview" in claim:
                            review = claim["claimReview"][0]
                            if "url" in review:
                                sources.append(review["url"])
    except Exception as e:
        print(f"[GoogleFactCheck] API error: {e}")

    return sources
