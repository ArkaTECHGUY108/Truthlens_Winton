import hashlib
import json
from datetime import datetime

def sign_record(payload: dict) -> dict:
    """
    Sign a record immutably with SHA-256 ledger hash.
    Accepts dict payloads (claim, verdict, sources, etc.).
    Produces a reproducible hash and timestamp.
    """
    # ✅ Ensure consistent ordering of dict keys before hashing
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))

    # ✅ Generate SHA-256 hash
    ledger_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

    return {
        "ledger_hash": ledger_hash,
        "signed_at": datetime.utcnow().isoformat(),
        "payload_preview": str(payload)[:200]  # optional debugging/tracing
    }
