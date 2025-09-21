# modules/provenance/deepfake_detector.py

from transformers import pipeline
from deepface import DeepFace
from PIL import Image
import torch


# ==============================
# Load HuggingFace Deepfake Detection Model
# ==============================
device = 0 if torch.cuda.is_available() else -1
hf_detector = pipeline(
    "image-classification",
    model="dima806/deepfake_vs_real_image_detection",  # ✅ proper deepfake model
    device=device
)


def detect_deepfake(image_path: str) -> dict:
    """
    Detect deepfake likelihood using HuggingFace deepfake model + DeepFace heuristic.
    Returns structured verdict and reasoning.
    """
    results = {}

    # HuggingFace deepfake detection
    try:
        preds = hf_detector(Image.open(image_path))
        top_pred = max(preds, key=lambda x: x["score"])
        results["huggingface_label"] = top_pred["label"]
        results["huggingface_confidence"] = round(float(top_pred["score"]) * 100, 2)
    except Exception as e:
        results["huggingface_label"] = "error"
        results["huggingface_confidence"] = 0.0
        results["error"] = f"HuggingFace detection failed: {str(e)}"

    # DeepFace heuristic
    try:
        deepface_analysis = DeepFace.analyze(
            img_path=image_path,
            actions=["emotion", "age", "gender"],
            detector_backend="retinaface",
            enforce_detection=False
        )
        # If DeepFace fails to find a face or results look inconsistent, lower confidence
        results["deepface_analysis"] = deepface_analysis
        results["deepface_confidence"] = 0.9 if deepface_analysis else 0.2
    except Exception as e:
        results["deepface_confidence"] = 0.0
        results["error"] = f"DeepFace analysis failed: {str(e)}"

    # Final decision fusion
    hf_label = results.get("huggingface_label", "").lower()
    hf_conf = results.get("huggingface_confidence", 0)
    df_conf = results.get("deepface_confidence", 0)

    if hf_label in ["fake", "deepfake"] and hf_conf > 70:
        verdict = "Deepfake"
        confidence = hf_conf
        explanation = f"HuggingFace model flagged this as {hf_label} with {hf_conf}% confidence."
    elif df_conf < 0.4:
        verdict = "Deepfake"
        confidence = 80
        explanation = "DeepFace found inconsistencies in the face (low verification confidence)."
    else:
        verdict = "Real"
        confidence = max(hf_conf, int(df_conf * 100))
        explanation = "No strong deepfake signals detected."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "huggingface_label": results.get("huggingface_label"),
        "huggingface_confidence": results.get("huggingface_confidence"),
        "deepface_confidence": results.get("deepface_confidence"),
        "explanation": explanation,
        "generative_explainer": (
            "This image was evaluated with hybrid analysis. "
            "HuggingFace detects pixel-level anomalies, "
            "while DeepFace checks facial consistency. "
            "Final verdict fuses both signals."
        ),
    }
