# modules/disinfo/disinfo_api.py
from fastapi import APIRouter, HTTPException
from core.schemas import VerdictResponse
from modules.disinfo.disinfo_logic import disinfo_pipeline

router = APIRouter()

@router.post("/disinfo", response_model=VerdictResponse)
async def classify_disinfo(payload: dict):
    """
    Disinformation Monitor API.
    Accepts a payload with factcheck, reasoning, and provenance.
    Returns a structured VerdictResponse.
    """
    try:
        factcheck = payload.get("factcheck", {})
        reasoning = payload.get("reasoning", {})
        provenance = payload.get("provenance", {})

        result = await disinfo_pipeline(factcheck, reasoning, provenance)
        return VerdictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
