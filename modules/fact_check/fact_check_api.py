# backend/api/fact_check_api.py

from fastapi import APIRouter, UploadFile, Form, HTTPException
from modules.reasoning.reasoning_logic import reasoning_pipeline
from modules.provenance.provenance_logic import provenance_pipeline
from services.ledger_service import sign_record
from services.gemini_client import gemini_fact_check_prompt, gemini_reasoning_prompt
from services.google_factcheck import query_factcheck_api
from modules.disinfo.social_connector import fetch_social_signals  # ✅ integrate social signals

router = APIRouter(prefix="/api", tags=["FactCheck"])

# In-memory store (replace with DB later if needed)
last_ledger = {"ledger_hash": None, "signed_at": None}
votes = {"agree": 0, "disagree": 0}


@router.post("/factcheck")
async def unified_factcheck(
    claim_text: str = Form(None),
    claim_url: str = Form(None),
    image: UploadFile = None
):
    """
    Main fact-checking endpoint.
    Runs Google FactCheck API + Gemini + reasoning + provenance + ledger + social signals.
    """

    # Ensure at least one input is provided
    if not claim_text and not claim_url and not image:
        raise HTTPException(status_code=400, detail="Provide claim_text, claim_url, or image.")

    # Pick main text for reasoning (priority: claim_text > claim_url > image.filename)
    main_claim = claim_text or claim_url or (image.filename if image else "Unknown claim")

    # 1. Get evidence from Google Fact Check API
    evidence = await query_factcheck_api(main_claim)

    # 2. Call Gemini fact-checker
    gemini_result = await gemini_fact_check_prompt(main_claim, evidence=evidence)

    # 3. Run Gemini Reasoning (fallacies, bias, debiased text, explainer)
    gemini_reasoning = await gemini_reasoning_prompt(main_claim)

    # 4. Run custom reasoning pipeline (your existing logic)
    custom_reasoning = await reasoning_pipeline(main_claim)

    # Safe merge of reasoning results
    reasoning = {
        "fallacy": (gemini_reasoning.get("fallacy") or []) + (custom_reasoning.get("fallacy") or []),
        "bias": (gemini_reasoning.get("bias") or []) + (custom_reasoning.get("bias") or []),
        "debiased_text": gemini_reasoning.get("debiased_text")
            or custom_reasoning.get("debiased_text")
            or main_claim,
        "explanation": gemini_reasoning.get("explanation")
            or custom_reasoning.get("explanation")
            or "",
        "generative_explainer": gemini_reasoning.get("generative_explainer") or "",
    }

    # 5. Run provenance pipeline
    provenance = await provenance_pipeline(main_claim)

    # 6. Fetch social signals (Twitter, YouTube, Facebook)
    social_signals = await fetch_social_signals(main_claim, limit=5)

    # 7. Create ledger record
    signed = sign_record(main_claim)
    global last_ledger
    last_ledger = signed

    # Build final response
    return {
        "verdict": gemini_result.get("verdict", "Unverified"),
        "confidence": gemini_result.get("confidence", 0),
        "relevant_sources": gemini_result.get("relevant_sources", evidence),
        "reasoning": reasoning,
        "provenance": provenance,
        "social_signals": social_signals,   # ✅ now included
        "ledger_status": signed,
    }


@router.post("/community/vote")
async def community_vote(vote: dict):
    """
    Record community agree/disagree votes.
    """
    global votes
    if vote["vote"] == "agree":
        votes["agree"] += 1
    else:
        votes["disagree"] += 1
    total = votes["agree"] + votes["disagree"]
    return {
        "agree": round(votes["agree"] / total * 100, 1) if total else 0,
        "disagree": round(votes["disagree"] / total * 100, 1) if total else 0,
    }


@router.get("/ledger/proof")
async def ledger_proof():
    """
    Get last recorded ledger hash.
    """
    return last_ledger or {"ledger_hash": None}