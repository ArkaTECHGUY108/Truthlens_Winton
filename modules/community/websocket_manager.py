from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    """
    Manages active WebSocket connections per claim_id.
    Allows broadcasting new votes and finalization events
    to all connected clients in real time.
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, claim_id: str, websocket: WebSocket):
        await websocket.accept()
        if claim_id not in self.active_connections:
            self.active_connections[claim_id] = []
        self.active_connections[claim_id].append(websocket)

    def disconnect(self, claim_id: str, websocket: WebSocket):
        if claim_id in self.active_connections:
            self.active_connections[claim_id].remove(websocket)
            if not self.active_connections[claim_id]:
                del self.active_connections[claim_id]

    async def broadcast(self, claim_id: str, message: dict):
        if claim_id in self.active_connections:
            for ws in self.active_connections[claim_id]:
                await ws.send_json(message)
