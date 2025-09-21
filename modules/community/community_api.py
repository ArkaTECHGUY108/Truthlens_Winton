from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from modules.community.community_logic import check_threshold_and_finalize
from modules.community.websocket_manager import WebSocketManager

router = APIRouter()

# In-memory store (replace with Redis/Postgres in production)
votes_db = {}   # {claim_id: [votes]}
ledger = []     # append-only ledger
ws_manager = WebSocketManager()

@router.websocket("/review/{claim_id}")
async def review_room(websocket: WebSocket, claim_id: str):
    """
    WebSocket endpoint for live community review of a claim.
    Clients join, cast votes, and receive real-time updates.
    """
    await ws_manager.connect(claim_id, websocket)
    if claim_id not in votes_db:
        votes_db[claim_id] = []

    try:
        while True:
            data = await websocket.receive_json()
            # Expecting: {"user": "Alice", "role": "journalist", "stance": "refute"}
            votes_db[claim_id].append(data)

            # Broadcast new vote to all participants
            await ws_manager.broadcast(claim_id, {"event": "new_vote", "vote": data})

            # Check thresholds
            finalized = check_threshold_and_finalize(claim_id, votes_db[claim_id], ledger)
            if finalized:
                await ws_manager.broadcast(claim_id, {"event": "finalized", "data": finalized})

    except WebSocketDisconnect:
        ws_manager.disconnect(claim_id, websocket)

@router.get("/ledger")
async def get_ledger():
    """
    View the append-only ledger with hashes and blockchain tx.
    """
    return {"ledger": ledger}
