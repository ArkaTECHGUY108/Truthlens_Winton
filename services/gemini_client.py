import google.generativeai as genai
import json
import re
import asyncio
from core.config import settings
from core.logger import setup_logger

logger = setup_logger()

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


# ------------------------------
# Utility: Safe JSON extractor
# ------------------------------
def clean_json_output(text: str) -> str:
    """Cleans Gemini output and extracts valid JSON string."""
    if not text:
        return "{}"
    # Remove markdown fences like ```json ... ```
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"```$", "", text.strip())
    return text.strip()


# ------------------------------
# Gemini Fact-Check Prompt
# ------------------------------
async def gemini_fact_check_prompt(claim: str, evidence: list[str]) -> dict:
    """
    Calls Gemini 2.5 Pro API with claim + retrieved evidence.
    Returns structured JSON verdict with retries and validation.
    """
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    You are a strict JSON generator.
    Evaluate the claim below using the provided evidence.
    Respond ONLY with valid JSON strictly matching this schema:
    {{
      "verdict": "True | False | Misleading | Unverified",
      "confidence": number (0-100),
      "reasoning": "string",
      "relevant_sources": ["list", "of", "strings"]
    }}

    Claim: {claim}
    Evidence: {evidence}
    """

    retries = 3
    for attempt in range(1, retries + 1):
        try:
            response = await model.generate_content_async(prompt)
            text_output = response.candidates[0].content.parts[0].text.strip()
            text_output = clean_json_output(text_output)

            parsed = json.loads(text_output)

            # Normalize confidence
            parsed["confidence"] = min(100, max(0, int(parsed.get("confidence", 0))))

            # Guarantee sources
            if not parsed.get("relevant_sources"):
                parsed["relevant_sources"] = evidence or []

            logger.info(f"[Gemini] Fact-check JSON parsed successfully (attempt {attempt}).")
            return parsed

        except json.JSONDecodeError as je:
            logger.warning(f"[Gemini] JSON parsing failed (attempt {attempt}): {je}")
        except Exception as e:
            logger.error(f"[Gemini] Fact-check API error (attempt {attempt}): {e}")

        await asyncio.sleep(2**attempt)  # exponential backoff

    # Final fallback
    return {
        "verdict": "Unverified",
        "confidence": 0,
        "reasoning": "Gemini API failed to return valid JSON.",
        "relevant_sources": evidence or [],
    }


# ------------------------------
# Gemini Reasoning Prompt
# ------------------------------
async def gemini_reasoning_prompt(claim: str) -> dict:
    """
    Uses Gemini 2.5 Pro to detect logical fallacies, biases,
    and generate a debiased version of the claim.
    Returns structured JSON with retries and validation.
    """
    model = genai.GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    Analyze the following claim for logical fallacies and biases.
    Respond ONLY in valid JSON strictly matching this schema:
    {{
      "fallacy": ["list of fallacies or []"],
      "bias": ["list of biases or []"],
      "debiased_text": "neutral rewritten version of the claim",
      "generative_explainer": "a short explanation in plain language"
    }}

    Claim: {claim}
    """

    retries = 3
    for attempt in range(1, retries + 1):
        try:
            response = await model.generate_content_async(prompt)
            text_output = response.candidates[0].content.parts[0].text.strip()
            text_output = clean_json_output(text_output)

            parsed = json.loads(text_output)

            # Ensure all keys exist
            parsed.setdefault("fallacy", [])
            parsed.setdefault("bias", [])
            parsed.setdefault("debiased_text", claim)
            parsed.setdefault("generative_explainer", "")

            logger.info(f"[Gemini] Reasoning JSON parsed successfully (attempt {attempt}).")
            return parsed

        except json.JSONDecodeError as je:
            logger.warning(f"[Gemini] Reasoning JSON parsing failed (attempt {attempt}): {je}")
        except Exception as e:
            logger.error(f"[Gemini] Reasoning API error (attempt {attempt}): {e}")

        await asyncio.sleep(2**attempt)

    # Final fallback
    return {
        "fallacy": [],
        "bias": [],
        "debiased_text": claim,
        "generative_explainer": "No explanation generated due to API failure.",
    }