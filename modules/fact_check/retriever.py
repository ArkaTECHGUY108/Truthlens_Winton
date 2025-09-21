from services.factcheck_client import fetch_factcheck_articles
from services.vector_store import search_similar, add_document, save_index
from modules.fact_check.news_client import fetch_news_articles
from modules.fact_check.wikipedia_client import fetch_wikipedia_snippets
from modules.fact_check.reddit_client import fetch_reddit_mentions
from modules.disinfo.social_connector import fetch_social_signals
from core.logger import setup_logger

logger = setup_logger()

async def retrieve_evidence(claim: str) -> list[str]:
    """
    Retrieve evidence for a claim using:
    - FAISS cache
    - FactCheck API
    - NewsAPI
    - Wikipedia
    - Reddit mentions
    - Social connectors (Twitter, YouTube, FB, IG)
    - Deduplication & normalization
    """
    evidence_pool = []

    # 1. FAISS Cache
    cached_results = search_similar(claim, top_k=3)
    for doc in cached_results:
        evidence_pool.append({
            "text": doc.get("text"),
            "url": doc.get("url", "cache"),
            "source": doc.get("source", "FAISS"),
            "timestamp": doc.get("timestamp", None)
        })

    # 2. FactCheck API
    try:
        api_results = await fetch_factcheck_articles(claim)
        for article in api_results:
            structured = {
                "text": article.get("text", ""),
                "url": article.get("url", ""),
                "source": "GoogleFactCheck",
                "timestamp": article.get("date", None)
            }
            if structured["text"]:
                evidence_pool.append(structured)
                add_document(structured["text"], url=structured["url"], source="GoogleFactCheck")
    except Exception as e:
        logger.error(f"FactCheck API error: {e}")

    # 3. NewsAPI
    try:
        news_results = await fetch_news_articles(claim, limit=3)
        for n in news_results:
            structured = {
                "text": f"{n.get('title', '')} - {n.get('description', '')}",
                "url": n.get("url", ""),
                "source": "NewsAPI",
                "timestamp": n.get("publishedAt", None)
            }
            if structured["text"]:
                evidence_pool.append(structured)
                add_document(structured["text"], url=structured["url"], source="NewsAPI")
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")

    # 4. Wikipedia
    try:
        wiki_results = await fetch_wikipedia_snippets(claim, limit=2)
        for w in wiki_results:
            structured = {
                "text": w.get("snippet", ""),
                "url": w.get("url", ""),
                "source": "Wikipedia",
                "timestamp": None
            }
            if structured["text"]:
                evidence_pool.append(structured)
                add_document(structured["text"], url=structured["url"], source="Wikipedia")
    except Exception as e:
        logger.error(f"Wikipedia fetch error: {e}")

    # 5. Reddit
    try:
        reddit_results = await fetch_reddit_mentions(claim, limit=2)
        if reddit_results:
            for r in reddit_results:
                structured = {
                    "text": r.get("title", "") + " " + r.get("text", ""),
                    "url": f"https://reddit.com/r/{r.get('subreddit', '')}",
                    "source": "Reddit",
                    "timestamp": r.get("created_utc", None)
                }
                if structured["text"]:
                    evidence_pool.append(structured)
                    add_document(structured["text"], url=structured["url"], source="Reddit")
        else:
            evidence_pool.append({"text": f"Mock Reddit discussion on {claim}", "url": "", "source": "Reddit", "timestamp": None})
    except Exception as e:
        logger.error(f"Reddit fetch error: {e}")
        evidence_pool.append({"text": f"Mock Reddit fallback: {claim}", "url": "", "source": "Reddit", "timestamp": None})

    # 6. Social signals
    try:
        social_results = await fetch_social_signals(claim, limit=2)
        for s in social_results:
            structured = {
                "text": s.get("text", ""),
                "url": s.get("url", ""),
                "source": s.get("platform", "Social"),
                "timestamp": s.get("timestamp", None)
            }
            if structured["text"]:
                evidence_pool.append(structured)
                add_document(structured["text"], url=structured["url"], source=structured["source"])
    except Exception as e:
        logger.error(f"Social signals fetch error: {e}")

    # Save FAISS
    save_index()

    # Deduplicate
    seen = set()
    merged = []
    for ev in evidence_pool:
        key = (ev["text"], ev["url"])
        if key not in seen and ev["text"]:
            seen.add(key)
            merged.append(ev)

    # Normalize & limit
    final_evidence = [
        f"{ev['text']} (Source: {ev['url']})"
        for ev in merged[:5]
    ]

    logger.info(f"Retrieved {len(final_evidence)} evidence items for claim.")
    return final_evidence
