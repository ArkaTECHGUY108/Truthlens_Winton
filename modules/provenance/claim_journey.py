import networkx as nx
from datetime import datetime
from modules.disinfo.social_connector import fetch_social_signals

async def build_claim_journey(claim_text: str, limit: int = 10) -> dict:
    """
    Build claim journey graph using multi-platform social signals.
    - Fetches mentions from Reddit, Twitter, YouTube, Facebook, Instagram.
    - Constructs graph: origin -> amplifiers -> fact-checkers.
    - Identifies top super-spreaders via degree centrality.
    """

    # ==============================
    # 1. Fetch signals
    # ==============================
    signals = await fetch_social_signals(claim_text, limit=limit)

    # If no signals found, return minimal mock journey
    if not signals:
        return {
            "claim_origin": "Unknown",
            "claim_amplifiers": [],
            "factcheck_intervention": ["Snopes", "PolitiFact", "FactCheck.org"],
            "super_spreaders": [],
            "graph_nodes": [],
            "graph_edges": []
        }

    # ==============================
    # 2. Extract origin + amplifiers
    # ==============================
    # First mention = origin (fallback = first signal)
    origin = signals[0]["user"]

    amplifiers = [s["user"] for s in signals if s["user"] != origin]

    # Fact-checkers (static for now, can be dynamic via FactCheck API)
    factcheckers = ["Snopes", "PolitiFact", "FactCheck.org"]

    # ==============================
    # 3. Build Graph
    # ==============================
    G = nx.DiGraph()

    # Add origin
    G.add_node(origin, role="origin", platform=signals[0]["platform"], timestamp=signals[0]["timestamp"])

    # Add amplifiers
    for s in signals:
        if s["user"] != origin:
            G.add_node(s["user"], role="amplifier", platform=s["platform"], timestamp=s["timestamp"])
            G.add_edge(origin, s["user"])

    # Add fact-checkers
    for fc in factcheckers:
        G.add_node(fc, role="factchecker", platform="FactCheck", timestamp=datetime.utcnow().isoformat())
        for amp in amplifiers:
            G.add_edge(amp, fc)

    # ==============================
    # 4. Identify Super-Spreaders
    # ==============================
    centrality = nx.degree_centrality(G)
    top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:3]
    super_spreaders = [n for n, _ in top_nodes if n not in factcheckers and n != origin]

    # ==============================
    # 5. Return Journey Dict
    # ==============================
    return {
        "claim_origin": origin,
        "claim_amplifiers": amplifiers,
        "factcheck_intervention": factcheckers,
        "super_spreaders": super_spreaders,
        "graph_nodes": [
            {"id": n, "role": G.nodes[n].get("role"), "platform": G.nodes[n].get("platform"), "timestamp": G.nodes[n].get("timestamp")}
            for n in G.nodes
        ],
        "graph_edges": list(G.edges)
    }
