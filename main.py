from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles   # ✅ NEW for serving frontend
from fastapi.responses import FileResponse    # ✅ For index.html fallback

from core.logger import setup_logger
from modules.orchestration.orchestrator import router as orchestration_router
from modules.disinfo.disinfo_api import router as disinfo_router
from modules.community.community_api import router as community_router
from modules.fact_check.fact_check_logic import fact_check_pipeline
from modules.provenance.provenance_logic import provenance_pipeline
from modules.reasoning.reasoning_logic import reasoning_pipeline
from modules.provenance.deepfake_detector import detect_deepfake
from services.ledger_service import sign_record
from modules.fact_check import fact_check_api

import shutil
import uuid
import os

# Initialize logger
logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="TruthLens Backend",
    description="Generative AI Misinformation Detection API with Fact-Check, Reasoning, Provenance, Deepfake Detection, Ledger, and Community Co-Verification",
    version="1.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(orchestration_router, prefix="/api", tags=["Orchestration"])
app.include_router(disinfo_router, prefix="/api", tags=["Disinformation Monitor"])
app.include_router(community_router, prefix="/api/community", tags=["Community Review"])
app.include_router(fact_check_api.router)


def prov_to_cytoscape(prov: dict) -> list[dict]:
    """Convert provenance JSON (nodes/edges) into Cytoscape.js elements"""
    elements = []
    for n in prov.get("nodes", []):
        elements.append({
            "data": {
                "id": n["id"],
                "label": n["id"],
                "role": n.get("role", "amplifier"),
                "platform": n.get("platform", ""),
                "timestamp": n.get("timestamp", "")
            }
        })
    for s, t in prov.get("edges", []):
        elements.append({"data": {"id": f"{s}->{t}", "source": s, "target": t}})
    return elements


@app.post("/api/factcheck")
async def unified_factcheck(
    claim_text: str = Form(None),
    claim_url: str = Form(None),
    image: UploadFile = File(None)
):
    """
    Unified entrypoint: accepts text, URL, or image.
    Runs Fact-Check, Reasoning, Provenance, Aegis, Ledger, Community engines.
    """

    try:
        logger.info("Received fact-check request")

        evidence = []
        verdict = "Unverified"
        confidence = 0
        reasoning_block = {}
        provenance = {}
        deepfake_result = None

        # Case 1: Text Claim
        if claim_text:
            fact_result = await fact_check_pipeline(claim_text)
            reasoning_result = await reasoning_pipeline(claim_text)
            provenance_result = await provenance_pipeline(claim_text)

            evidence = fact_result.get("relevant_sources", [])
            verdict = fact_result.get("verdict", "Unverified")
            confidence = fact_result.get("confidence", 0)
            reasoning_block = {
                "explanation": reasoning_result.get("explanation", ""),
                "fallacy": reasoning_result.get("fallacy", []),
                "bias": reasoning_result.get("bias", []),
                "debiased_text": reasoning_result.get("debiased_text", ""),
                "reasoning_confidence": reasoning_result.get("reasoning_confidence", 0)
            }
            provenance = provenance_result

        # Case 2: Claim URL
        elif claim_url:
            fact_result = await fact_check_pipeline(claim_url)
            provenance_result = await provenance_pipeline(claim_url)

            evidence = fact_result.get("relevant_sources", [])
            verdict = fact_result.get("verdict", "Unverified")
            confidence = fact_result.get("confidence", 0)
            reasoning_block = {
                "explanation": "Checked via URL context.",
                "fallacy": [],
                "bias": [],
                "debiased_text": "",
                "reasoning_confidence": 0
            }
            provenance = provenance_result

        # Case 3: Image Upload
        elif image:
            temp_filename = f"/tmp/{uuid.uuid4()}_{image.filename}"
            with open(temp_filename, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            deepfake_result = detect_deepfake(temp_filename)
            provenance_result = await provenance_pipeline(temp_filename)

            verdict = "Manipulated" if deepfake_result.get("manipulated") else "Authentic"
            confidence = deepfake_result.get("confidence", 80)
            reasoning_block = {
                "explanation": deepfake_result.get("explanation", "Image forensic analysis."),
                "fallacy": [],
                "bias": [],
                "debiased_text": "",
                "reasoning_confidence": confidence
            }
            provenance = provenance_result
            os.remove(temp_filename)

        # Ledger Write
        ledger_entry = {
            "claim_text": claim_text,
            "claim_url": claim_url,
            "verdict": verdict,
            "confidence": confidence,
            "sources": evidence,
            "provenance": provenance
        }
        ledger = sign_record(ledger_entry)

        # Add Cytoscape graph
        provenance["elements"] = prov_to_cytoscape(provenance.get("provenance_graph", {}))

        return {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning_block,
            "relevant_sources": evidence,
            "provenance": provenance,
            "deepfake": deepfake_result,
            "ledger_status": ledger
        }

    except Exception as e:
        logger.exception(f"FactCheck pipeline error: {e}")
        return {
            "error": str(e),
            "verdict": "Unverified",
            "confidence": 0,
            "reasoning": {
                "explanation": "Pipeline error occurred.",
                "fallacy": [],
                "bias": [],
                "debiased_text": "",
                "reasoning_confidence": 0
            }
        }


@app.get("/health")
async def health_check():
    logger.info("Health check pinged")
    return {"status": "ok", "message": "TruthLens backend running!"}


# ✅ Serve static frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="static")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))