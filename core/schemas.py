from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime

# ==============================
# Input schema for /claims
# ==============================
class ClaimRequest(BaseModel):
    claim_text: Optional[str] = None
    claim_url: Optional[HttpUrl] = None
    media_file: Optional[str] = None  # future: file upload support


# ==============================
# Provenance Graph Schemas
# ==============================
class ProvenanceNode(BaseModel):
    id: str
    role: str
    platform: Optional[str] = None
    timestamp: Optional[str] = None

class ProvenanceGraph(BaseModel):
    nodes: List[ProvenanceNode]
    edges: List[List[str]]  # each edge = [source, target]


# ==============================
# Unified Verdict + Reasoning + Provenance Schema
# ==============================
class VerdictResponse(BaseModel):
    claim: str
    verdict: str  # True, False, Misleading, Manipulated, Unverified
    confidence: float
    sources: List[str]

    # Fact-Check Engine advanced fields
    supporting_evidence: Optional[List[Dict]] = None
    counter_evidence: Optional[List[Dict]] = None
    timeline: Optional[List[Dict]] = None
    fusion_confidence: Optional[int] = None

    # Reasoning Engine outputs
    fallacy: Optional[List[str]] = None        # list of detected fallacies
    bias: Optional[List[str]] = None           # list of detected biases
    debiased_text: Optional[str] = None
    reasoning_confidence: Optional[int] = None  # reliability of reasoning

    # Provenance Engine outputs
    authenticity_score: Optional[int] = None
    deepfake_flags: Optional[List[str]] = None
    metadata_flags: Optional[List[str]] = None
    claim_origin: Optional[str] = None
    claim_amplifiers: Optional[List[str]] = None
    factcheck_intervention: Optional[List[str]] = None
    super_spreaders: Optional[List[str]] = None
    provenance_graph: Optional[ProvenanceGraph] = None   # ✅ structured model

    # Explainers
    emotion_score: Optional[int] = None
    provenance: Optional[Dict] = None   # can still store raw provenance dict
    trajectory: Optional[Dict] = None
    explainer: Optional[str] = None


# ==============================
# Community Co-Verification Schemas
# ==============================
class VoteIn(BaseModel):
    user: str
    role: str   # contributor | journalist | fact-checker
    stance: str # support | refute | misleading


class VoteRecord(VoteIn):
    timestamp: str


class ReviewRoom(BaseModel):
    claim_id: str
    votes: List[VoteRecord]
    finalized: bool
    final_verdict: Optional[VerdictResponse]


class LedgerRecord(BaseModel):
    claim_id: str
    verdict: str
    confidence: float
    sources: List[str]
    explainer: str
    ledger_hash: str
    votes: List[VoteRecord]
    finalized_at: datetime
