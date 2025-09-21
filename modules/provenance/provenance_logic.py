from modules.provenance.deepfake_detector import detect_deepfake
from modules.provenance.metadata_validator import validate_metadata
from modules.provenance.claim_journey import build_claim_journey


async def provenance_pipeline(claim_text: str, media_file: str = None) -> dict:
    """
    Provenance Engine:
    - Deepfake detection (HuggingFace + DeepFace hybrid).
    - Metadata validation (EXIF, C2PA if supported).
    - Claim journey (origin → amplifiers → fact-checkers).
    - Graph analysis to identify super-spreaders.
    Returns a compact structured dictionary for VerdictResponse.
    """

    # ==============================
    # 1. Deepfake + Metadata Checks
    # ==============================
    try:
        if media_file:
            deepfake_result = detect_deepfake(media_file)
            metadata_result = validate_metadata(media_file)
        else:
            deepfake_result = {
                "flagged_as_deepfake": False,
                "huggingface_confidence": 0.0,
                "deepface_confidence": 1.0
            }
            metadata_result = {"metadata_flags": ["No media provided"]}
    except Exception as e:
        deepfake_result = {"flagged_as_deepfake": False, "error": str(e)}
        metadata_result = {"metadata_flags": [f"Metadata check failed: {str(e)}"]}

    # ==============================
    # 2. Claim Journey (async call)
    # ==============================
    try:
        journey = await build_claim_journey(claim_text)
    except Exception as e:
        journey = {
            "claim_origin": "Unknown",
            "claim_amplifiers": [],
            "factcheck_intervention": [],
            "graph_nodes": [],
            "graph_edges": [],
            "super_spreaders": [],
            "error": f"Journey mapping failed: {str(e)}"
        }

    # ==============================
    # 3. Authenticity Score
    # ==============================
    authenticity_score = 100
    if deepfake_result.get("flagged_as_deepfake"):
        authenticity_score -= 50
    if (
        metadata_result.get("metadata_flags")
        and "No media provided" not in metadata_result["metadata_flags"]
    ):
        authenticity_score -= 10 * len(metadata_result["metadata_flags"])

    authenticity_score = max(0, min(100, authenticity_score))

    # ==============================
    # 4. Compact Structured Output
    # ==============================
    provenance_output = {
        "authenticity_score": authenticity_score,
        "deepfake_flags": (
            [f"Deepfake suspected with {deepfake_result.get('huggingface_confidence', 0)*100:.1f}% HuggingFace confidence"]
            if deepfake_result.get("flagged_as_deepfake") else []
        ),
        "metadata_flags": metadata_result.get("metadata_flags", []),
        "claim_origin": journey.get("claim_origin"),
        "claim_amplifiers": journey.get("claim_amplifiers", []),
        "factcheck_intervention": journey.get("factcheck_intervention", []),
        "provenance_graph": {
            "nodes": journey.get("graph_nodes", []),
            "edges": journey.get("graph_edges", [])
        },
        "super_spreaders": journey.get("super_spreaders", [])
    }

    return provenance_output
