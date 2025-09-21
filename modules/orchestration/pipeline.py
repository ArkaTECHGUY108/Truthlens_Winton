from core.schemas import (
    ClaimRequest,
    VerdictResponse,
    ProvenanceGraph,
    ProvenanceNode,
)
from modules.fact_check.fact_check_logic import fact_check_pipeline
from modules.reasoning.reasoning_logic import reasoning_pipeline
from modules.provenance.provenance_logic import provenance_pipeline
from core.logger import setup_logger

logger = setup_logger()


async def process_claim(claim: ClaimRequest) -> VerdictResponse:
    """
    Orchestrates Fact-Check Engine + Reasoning Engine + Provenance Engine.
    Returns a unified VerdictResponse with all fields populated,
    including trajectory timeline.
    """
    input_text: str = claim.claim_text or claim.claim_url or "Media File"

    # ==============================
    # 1. Fact-Check Engine
    # ==============================
    try:
        factcheck_result = await fact_check_pipeline(input_text)
    except Exception as e:
        logger.error(f"Fact-check engine failed: {e}")
        factcheck_result = {"verdict": "Unverified", "confidence": 0, "relevant_sources": []}

    # ==============================
    # 2. Reasoning Engine
    # ==============================
    try:
        reasoning_result = await reasoning_pipeline(input_text)
    except Exception as e:
        logger.error(f"Reasoning engine failed: {e}")
        reasoning_result = {"fallacy": [], "bias": [], "debiased_text": input_text, "reasoning_confidence": 0}

    # ==============================
    # 3. Provenance Engine
    # ==============================
    try:
        provenance_result = await provenance_pipeline(input_text, claim.media_file)
    except Exception as e:
        logger.error(f"Provenance engine failed: {e}")
        provenance_result = {
            "authenticity_score": None,
            "deepfake_flags": [],
            "metadata_flags": [],
            "claim_origin": None,
            "claim_amplifiers": [],
            "factcheck_intervention": [],
            "super_spreaders": [],
            "provenance_graph": {"nodes": [], "edges": []},
        }

    # ==============================
    # 4. Convert provenance graph into structured model
    # ==============================
    graph_data = provenance_result.get("provenance_graph", {})
    provenance_graph = None
    trajectory = None

    if graph_data and "nodes" in graph_data and "edges" in graph_data:
        provenance_graph = ProvenanceGraph(
            nodes=[
                ProvenanceNode(
                    id=n.get("id"),
                    role=n.get("role"),
                    platform=n.get("platform"),
                    timestamp=n.get("timestamp"),
                )
                for n in graph_data.get("nodes", [])
            ],
            edges=graph_data.get("edges", []),
        )

        # ==============================
        # 5. Build trajectory timeline
        # ==============================
        sorted_nodes = sorted(
            provenance_graph.nodes,
            key=lambda n: n.timestamp or "",
        )

        timeline = []
        for node in sorted_nodes:
            action = (
                "Claim originated"
                if node.role == "origin"
                else "Amplified claim"
                if node.role == "amplifier"
                else "Fact-checked and debunked"
                if node.role == "factchecker"
                else "Observed activity"
            )
            timeline.append(
                {
                    "actor": node.id,
                    "role": node.role,
                    "platform": node.platform,
                    "time": node.timestamp,
                    "action": action,
                }
            )

        trajectory = {"timeline": timeline}

    # ==============================
    # 6. Merge into unified response
    # ==============================
    result = VerdictResponse(
        # Core
        claim=input_text,
        verdict=factcheck_result.get("verdict", "Unverified"),
        confidence=factcheck_result.get("confidence", 0),
        sources=factcheck_result.get("relevant_sources", []),

        # Explainer
        explainer=factcheck_result.get("reasoning", "No explanation available."),

        # Reasoning
        fallacy=reasoning_result.get("fallacy", []),
        bias=reasoning_result.get("bias", []),
        debiased_text=reasoning_result.get("debiased_text", None),
        reasoning_confidence=reasoning_result.get("reasoning_confidence", 50),

        # Provenance
        authenticity_score=provenance_result.get("authenticity_score"),
        deepfake_flags=provenance_result.get("deepfake_flags", []),
        metadata_flags=provenance_result.get("metadata_flags", []),
        claim_origin=provenance_result.get("claim_origin"),
        claim_amplifiers=provenance_result.get("claim_amplifiers", []),
        factcheck_intervention=provenance_result.get("factcheck_intervention", []),
        super_spreaders=provenance_result.get("super_spreaders", []),
        provenance_graph=provenance_graph,

        # Reserved / extension fields
        emotion_score=None,
        provenance=provenance_result,   # raw dict for debug/logs
        trajectory=trajectory,
    )

    return result
