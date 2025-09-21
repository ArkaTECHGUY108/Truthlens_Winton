
🔍 TruthLens – AI-Powered Fact-Checking Platform

TruthLens is an AI-powered misinformation detection and provenance-tracking system.
It combines Generative AI, Deepfake Detection, Ledger Anchoring, and Community Co-Verification to combat fake news at scale.


🚀 Features

🧠 Fact-Check Engine – Multi-source claim verification using LLMs + search.

🔗 Provenance Graphs – Track amplification paths of misinformation.

🛡 Deepfake Detection – Detect manipulated images/videos with DeepFace + Transformers.

📜 Blockchain Ledger – Anchor fact-check verdicts on-chain for transparency.

🤝 Community Co-Verification – Human-in-the-loop voting + AI hybrid scoring.

📡 Social Signal Tracking – Analyze narrative spread across Twitter, YouTube, Reddit.

🎨 Frontend (Vercel) – Neon glassmorphism dashboard for users.

⚡ Backend (FastAPI) – Modular Python service deployable on Render / Fly.io / GCP Run.



---

📂 Project Structure

truthlens-backend/
│── core/                # Logging, config, schemas
│── modules/             # Engines: fact_check, provenance, disinfo, reasoning, community
│── services/            # External services (Gemini, OpenAI, Ledger, Vector DB)
│── frontend/            # Static frontend (HTML, CSS, JS) served via FastAPI
│── tests/               # Unit tests
│── main.py              # FastAPI entrypoint
│── requirements.txt     # Dependencies
│── Dockerfile           # Container for deployment
│── .gitignore
│── README.md


---

⚙ Installation (Local Development)

1. Clone the repo:

git clone https://github.com/ArkaTECHGUY108/Truthlens_Winton.git
cd truthlens-backend


2. Create & activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows


3. Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt


4. Run locally:

uvicorn main:app --reload --port 8080


5. Open frontend/index.html.


🌍 Deployment

1. Render (Initial Attempt ❌)

❌ Issue: Render build failed due to faiss-cpu and sentence-transformers requiring Rust/Cargo compilation.

✅ Fix: Pinned versions with prebuilt wheels (faiss-cpu==1.7.4, sentence-transformers==2.2.2).


2. Google Cloud Run (Attempt ⚠)

❌ Issue: Cloud Run revision failed (PORT=8080 not served).

Root cause: uvicorn not properly configured in Dockerfile.

✅ Fix: Explicit CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"].


3. Fly.io (Recommended ✅)

Lightweight VM with persistent volume support.

Works well for FastAPI + static frontend.

Deployment steps:

fly launch
fly deploy
fly logs


4. Frontend (Vercel ✅)

Deploy frontend/ folder separately.

Set NEXT_PUBLIC_BACKEND_URL or API_URL env var to point to backend (Fly.io / Cloud Run).


🛑 API Challenges

Google Gemini API

⚠ Rate limits (60 RPM free).

❌ Long context inputs truncated → need chunking.


OpenAI Whisper API

⚠ Audio file size limits.

❌ Long inference time for .wav uploads.


Social Media APIs

❌ Twitter/X API requires paid tier for search.

⚠ Reddit API rate limits when fetching threads.


📈 Future Prospects

🌐 Multilingual Fact-Checking (Hindi, Bengali, Bhojpuri).

🔗 Web3 Provenance Ledger with C2PA compliance.

🎥 Real-Time Deepfake Defense (video stream detection).

🤖 Agentic Fact-Checkers – AI agents monitoring different domains.

📊 Analytics Dashboard for policymakers + journalists.

🚀 Scalable Deployment using Kubernetes (GKE / EKS).


🧪 Testing

Run backend tests:

uvicorn main:app --reload --host 0.0.0.0 --port 8080


🧑‍💻 Contributors

👨‍💻 Team WINTON

Arka Chakraborty – Lead Backend Engineer

Mainak Pal – AI/ML & Web3 Specialist

Rudrava Tripathi – Frontend Architect

Aniruddha Bera – AIML Specialist

Sourav Kundu – Backend & Integration
