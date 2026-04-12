"""
RapidAid - AI Guide Routes
Real-time first aid guidance powered by Google Gemini AI (FREE).
"""

from flask import Blueprint, request, jsonify, session
from services.ai_service import get_ai_firstaid, get_ai_chat_response
from database.db import get_db
import os

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/guide", methods=["POST"])
def ai_guide():
    data      = request.get_json() or {}
    emergency = data.get("emergency", "general").lower().strip()
    lang      = data.get("lang", "en")
    context   = data.get("context", "")

    valid_types = {"burns", "bleeding", "fracture", "choking", "heart", "drowning"}
    if emergency not in valid_types:
        return jsonify({"success": False, "message": f"Unknown emergency type: {emergency}"}), 400

    result = get_ai_firstaid(emergency, lang, context)

    if "user_id" in session and result.get("success"):
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO history (user_id, emergency_type, action, language) VALUES (%s, %s, %s, %s)",
                (session["user_id"], emergency, "AI guidance viewed", lang)
            )
            db.commit()
            cursor.close()
        except Exception:
            pass

    return jsonify(result)


@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    data      = request.get_json() or {}
    message   = data.get("message", "").strip()
    emergency = data.get("emergency", "")
    lang      = data.get("lang", "en")

    if not message:
        return jsonify({"success": False, "message": "Message is required."}), 400
    if len(message) > 500:
        return jsonify({"success": False, "message": "Message too long (max 500 chars)."}), 400

    result = get_ai_chat_response(message, emergency, lang)
    return jsonify(result)


@ai_bp.route("/status", methods=["GET"])
def ai_status():
    key_set = bool(os.environ.get("HF_TOKEN"))
    return jsonify({
        "available": key_set,
        "provider":  "Hugging Face (Qwen2.5-72B)",
        "message":   "AI ready" if key_set else "Add HF_TOKEN to .env to enable AI guidance"
    })
