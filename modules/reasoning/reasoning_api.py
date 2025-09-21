from fastapi import APIRouter
from core.schemas import ClaimRequest, ReasoningResponse
from modules.reasoning.reasoning_logic import reasoning_pipeline

router = APIRouter(prefix="/api/reasoning", tags=["Reasoning Engine"])

@router.post("/", response_model=ReasoningResponse)
async def analyze_reasoning(claim: ClaimRequest):
    return await reasoning_pipeline(claim.claim_text)
