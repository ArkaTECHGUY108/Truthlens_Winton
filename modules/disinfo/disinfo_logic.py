# modules/disinfo/disinfo_logic.py

async def disinfo_pipeline(factcheck: dict, reasoning: dict, provenance: dict) -> dict:
    """
    Combines fact-check, reasoning, and provenance analysis
    to flag disinformation narratives and virality.
    """
    disinfo_flags = []
    narrative_cluster = None
    virality_score = 10

    # Example logic — expand later
    if "nasa" in factcheck.get("verdict", "").lower():
        disinfo_flags.append("Matches recurring NASA blackout hoax")
        narrative_cluster = "NASA blackout hoax"
        virality_score = 80

    if reasoning.get("fallacy"):
        disinfo_flags.append(f"Fallacies detected: {', '.join(reasoning['fallacy'])}")

    if provenance.get("claim_amplifiers"):
        amplifiers_count = len(provenance["claim_amplifiers"])
        if amplifiers_count > 2:
            disinfo_flags.append("Amplified by multiple accounts")
            virality_score += amplifiers_count * 5

    return {
        "claim": factcheck.get("claim", "Unknown"),
        "verdict": factcheck.get("verdict", "Unverified"),
        "confidence": factcheck.get("confidence", 0),
        "sources": factcheck.get("sources", []),
        "fallacy": reasoning.get("fallacy", []),
        "bias": reasoning.get("bias", []),
        "debiased_text": reasoning.get("debiased_text", None),
        "reasoning_confidence": reasoning.get("reasoning_confidence", 50),
        "authenticity_score": provenance.get("authenticity_score"),
        "deepfake_flags": provenance.get("deepfake_flags", []),
        "metadata_flags": provenance.get("metadata_flags", []),
        "claim_origin": provenance.get("claim_origin"),
        "claim_amplifiers": provenance.get("claim_amplifiers", []),
        "factcheck_intervention": provenance.get("factcheck_intervention", []),
        "super_spreaders": provenance.get("super_spreaders", []),
        "provenance_graph": provenance.get("provenance_graph", {}),
        "explainer": (
            f"Disinformation Monitor flagged this claim. "
            f"Cluster: {narrative_cluster}, Flags: {disinfo_flags}"
        ),
    }
