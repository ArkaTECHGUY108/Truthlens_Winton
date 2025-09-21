from services.gemini_client import gemini_reasoning_prompt
from modules.reasoning.fallacy_patterns import detect_patterns
from core.logger import setup_logger

logger = setup_logger()

async def reasoning_pipeline(claim: str) -> dict:
    """
    Advanced Reasoning Engine with Confidence Scoring:
    - Regex fallacy & bias detection
    - Gemini reasoning analysis
    - Merge results, deduplicate, and normalize
    - Confidence score (0–100)
    """
    # ----------------------------
    # Step 1: Regex Pattern Detection
    # ----------------------------
    pattern_results = detect_patterns(claim)
    regex_fallacies = pattern_results.get("fallacies", [])
    regex_biases = pattern_results.get("biases", [])

    # ----------------------------
    # Step 2: Gemini Reasoning
    # ----------------------------
    try:
        llm_result = await gemini_reasoning_prompt(claim)
        llm_fallacies = llm_result.get("fallacy", [])
        llm_biases = llm_result.get("bias", [])
        debiased_text = llm_result.get("debiased_text", claim)
    except Exception as e:
        logger.error(f"Gemini reasoning failed: {str(e)}")
        llm_fallacies, llm_biases, debiased_text = [], [], claim

    # ----------------------------
    # Step 3: Merge + Deduplicate
    # ----------------------------
    combined_fallacies = sorted(list(set(regex_fallacies + llm_fallacies)))
    combined_biases = sorted(list(set(regex_biases + llm_biases)))

    # ----------------------------
    # Step 4: Confidence Scoring
    # ----------------------------
    confidence = 50  # base confidence

    # Boost if regex found matches
    if regex_fallacies or regex_biases:
        confidence += 15

    # Boost if Gemini found matches
    if llm_fallacies or llm_biases:
        confidence += 20

    # Boost if both sources agree
    if set(regex_fallacies) & set(llm_fallacies) or set(regex_biases) & set(llm_biases):
        confidence += 15

    # Cap to [0, 100]
    confidence = min(confidence, 100)

    # ----------------------------
    # Step 5: Return Structured Output
    # ----------------------------
    result = {
        "fallacy": combined_fallacies if combined_fallacies else None,
        "bias": combined_biases if combined_biases else None,
        "debiased_text": debiased_text,
        "reasoning_confidence": confidence
    }

    logger.info(f"Reasoning Engine Output: {result}")
    return result
