"""SatarkAI: local-first screening demo; never visits user-provided URLs."""
from __future__ import annotations

import os
import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(os.environ.get("SATARKAI_MODEL_PATH", BASE_DIR / "ml" / "model.joblib"))
app = Flask(__name__)
LOCAL_ONLY = os.environ.get("SATARKAI_PUBLIC_DEPLOY", "0") != "1"

RULES = [
    ("Urgent language", [r"\burgent\b", r"immediately", r"right now", r"within\s+\d+\s*(?:min|hour)", r"jaldi", r"turant", r"abhi", r"aaj hi", r"last chance", r"expires? today"], "Message aapse jaldi action lene ka pressure bana sakta hai."),
    ("Account threat", [r"account.{0,30}(?:block|suspend| band| बंद| बंद हो| बंद कर)", r"(?:block|suspend| band| बंद).{0,30}account", r"account.{0,30}verify", r"kyc.{0,30}(?: band|expire|block)", r"account will be closed"], "Message account band ya suspend hone ki warning de raha hai."),
    ("Credential request", [r"\botp\b", r"password", r"pin\b", r"cvv\b", r"\b(?:share|send|batao).{0,20}(?:otp|password|pin)"], "Message sensitive login ya payment details maang sakta hai."),
    ("Payment pressure", [r"\bpay(?:ment)?\b", r"transfer money", r"send money", r"processing fee", r"prize.{0,30}fee", r"इनाम.{0,30}शुल्क", r"upi"], "Message payment ya paise transfer karne ko keh sakta hai."),
    ("Impersonation clue", [r"\b(?:bank|police|customs|courier|income tax|rbi)\b", r"customer care", r"support team", r"government"], "Message kisi organization ya authority ka naam use karta hai; independently verify karein."),
]
URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"']+", re.I)

try:
    import joblib
    _MODEL = joblib.load(MODEL_PATH) if MODEL_PATH.is_file() else None
except Exception:
    _MODEL = None


@app.get("/")
def home():
    return render_template("index.html", local_only=LOCAL_ONLY)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SatarkAI", "analyzer": "ml+rules" if _MODEL else "rules-fallback", "ml_available": _MODEL is not None})


@app.post("/api/analyze-message")
def analyze_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": 'JSON body bhejein, jaise {"message": "..."}.'}), 400
    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "Message text ke roop mein bhejein."}), 400
    message = message.strip()
    if not message:
        return jsonify({"error": "Pehle message paste karein."}), 400
    if len(message) > 10000:
        return jsonify({"error": "Message 10,000 characters se chhota rakhein."}), 413

    indicators = []
    for signal, patterns, reason in RULES:
        if any(re.search(pattern, message, re.I) for pattern in patterns):
            indicators.append({"signal": signal, "reason": reason})
    if URL_RE.search(message):
        indicators.append({"signal": "Link present", "reason": "Message mein link hai. SatarkAI ne URL ko open ya fetch nahi kiya; legitimacy independently verify karein."})

    ml_prediction, confidence = None, None
    if _MODEL is not None:
        try:
            ml_prediction = str(_MODEL.predict([message])[0])
            probabilities = _MODEL.predict_proba([message])[0]
            confidence = round(float(max(probabilities)), 3)
        except Exception:
            # Corrupt/incompatible artifacts never stop the rule-based analyzer.
            ml_prediction, confidence = None, None

    rule_count = len(indicators)
    if rule_count >= 3 or (ml_prediction == "suspicious" and confidence is not None and confidence >= 0.62):
        risk = "High"
    elif rule_count >= 1 or ml_prediction == "suspicious":
        risk = "Elevated"
    else:
        risk = "No obvious indicators"
    explanation = f"{rule_count} rule-based warning indicator{'s' if rule_count != 1 else ''} mile hain."
    if ml_prediction is not None:
        explanation += f" ML prototype ka label: {ml_prediction} (confidence {confidence:.0%})."
    elif rule_count == 0:
        explanation = "Is basic check mein koi configured warning phrase nahi mila. ML model unavailable hai; rule-based fallback use hua."
    return jsonify({
        "risk_assessment": risk,
        "explanation": explanation,
        "indicators": indicators,
        "recommended_actions": ["Message ke link se login ya payment mat karo.", "OTP aur password kisi ke saath share mat karo.", "Claim ko official app ya independently verified contact se check karo."],
        "limitations": "SatarkAI ek demo screening tool hai. ML model chhote, hand-curated dataset par train hua hai; output fraud ka proof nahi aur safety ki guarantee bhi nahi. URL ko sirf text ke roop mein check kiya jata hai; koi URL open/fetch nahi hota. ML artifact unavailable ho to rules fallback chalte hain.",
        "ml": {"available": ml_prediction is not None, "prediction": ml_prediction, "confidence": confidence},
        "url_checked": False,
    })


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "5000")), debug=False)
