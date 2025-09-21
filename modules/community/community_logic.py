import time
from modules.community.ledger import generate_hash, anchor_to_blockchain

# Thresholds for consensus snapshots
VOTE_THRESHOLDS = [10, 50, 100]

# Role weights
ROLE_WEIGHTS = {
    "contributor": 1,
    "journalist": 2,
    "fact-checker": 3
}

def calculate_consensus(votes: list[dict]) -> tuple[str, float]:
    """
    Calculate weighted consensus from votes.
    """
    weighted = {}
    for v in votes:
        stance = v["stance"].lower()
        weight = ROLE_WEIGHTS.get(v["role"].lower(), 1)
        weighted[stance] = weighted.get(stance, 0) + weight

    if not weighted:
        return "Unverified", 0.0

    final_stance = max(weighted, key=weighted.get)
    confidence = (weighted[final_stance] / sum(weighted.values())) * 100
    return final_stance.title(), confidence

def check_threshold_and_finalize(claim_id: str, votes: list[dict], ledger: list[dict]):
    """
    Checks if a threshold has been reached and finalizes consensus.
    Generates SHA256 hash and anchors it to blockchain.
    """
    count = len(votes)
    if count in VOTE_THRESHOLDS:
        verdict, confidence = calculate_consensus(votes)
        payload = {
            "claim_id": claim_id,
            "verdict": verdict,
            "confidence": confidence,
            "votes": votes,
            "threshold": count,
            "timestamp": time.time(),
        }
        payload["ledger_hash"] = generate_hash(payload)
        payload["blockchain_tx"] = anchor_to_blockchain(payload["ledger_hash"])
        ledger.append(payload)
        return payload
    return None
