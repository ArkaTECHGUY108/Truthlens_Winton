from services.gemini_client import gemini_fact_check_prompt
from modules.fact_check.retriever import retrieve_evidence
from core.logger import setup_logger

logger = setup_logger()

async def fact_check_pipeline(claim: str) -> dict:
    """
    Main fact-check pipeline:
    - Retrieve evidence
    - Ask Gemini
    - Normalize + fallback confidence
    """
    try:
        evidence = await retrieve_evidence(claim)

        if not evidence:
            return {
                "verdict": "Unverified",
                "confidence": 0,
                "reasoning": "No evidence found.",
                "relevant_sources": []
            }

        result = await gemini_fact_check_prompt(claim, evidence)

        confidence = result.get("confidence", 0)
        try:
            if isinstance(confidence, str) and confidence.endswith("%"):
                confidence = float(confidence.strip("%"))
            confidence = float(confidence)
        except Exception:
            confidence = 0

        if 0 <= confidence <= 5:
            confidence *= 20

        # Fallback scaling: if still low, boost with reasoning
        if confidence < 30 and result.get("reasoning"):
            confidence += 20
        if confidence < 50 and "authenticity_score" in result:
            confidence += result["authenticity_score"] / 10

        confidence = min(100, confidence)

        return {
            "verdict": result.get("verdict", "Unverified"),
            "confidence": confidence,
            "reasoning": result.get("reasoning", "No explanation available."),
            "relevant_sources": result.get("relevant_sources", evidence)
        }

    except Exception as e:
        logger.exception(f"[FactCheck] Pipeline failed for claim: {claim} | Error: {e}")
        return {
            "verdict": "Unverified",
            "confidence": 0,
            "reasoning": f"Fact-check pipeline error: {e}",
            "relevant_sources": []
        }
