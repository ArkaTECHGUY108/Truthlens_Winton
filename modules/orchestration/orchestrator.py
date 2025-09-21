from fastapi import APIRouter, HTTPException
from core.schemas import ClaimRequest, VerdictResponse
from modules.orchestration.pipeline import process_claim
from uuid import uuid4

router = APIRouter()

# In-memory store for claims and verdicts (replace with DB later)
claims_store = {}  # claim_id -> VerdictResponse


@router.post("/claims")
async def submit_claim(claim: ClaimRequest):
    """
    Submit a claim for AI fact-checking + reasoning + provenance.
    Returns a claim_id and the unified verdict object.
    """
    if not (claim.claim_text or claim.claim_url or claim.media_file):
        raise HTTPException(status_code=400, detail="No claim provided")

    # Process claim via pipeline
    result: VerdictResponse = await process_claim(claim)

    # Generate claim_id
    claim_id = str(uuid4())

    # Store result in memory
    claims_store[claim_id] = result.dict()

    # Return wrapped response with claim_id
    return {
        "claim_id": claim_id,
        "verdict": result
    }


@router.get("/verdicts/{claim_id}", response_model=VerdictResponse)
async def get_verdict(claim_id: str):
    """
    Retrieve the verdict for a given claim_id.
    """
    if claim_id not in claims_store:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claims_store[claim_id]
