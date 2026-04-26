"""
RapidAid - History Routes
MySQL version — uses %s placeholders
"""

from flask import Blueprint, jsonify, session
from database.db import get_db

history_bp = Blueprint("history", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Login required."}), 401
        return f(*args, **kwargs)
    return decorated


@history_bp.route("/", methods=["GET"])
@login_required
def get_history():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        """SELECT emergency_type, action, language, created_at
           FROM history
           WHERE user_id = %s
           ORDER BY created_at DESC
           LIMIT 50""",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()

    ICONS = {
        "burns": "🔥", "bleeding": "🩸", "fracture": "🦴",
        "choking": "😮‍💨", "heart": "❤️", "drowning": "🌊", "PANIC_MODE": "🚨"
    }

    history = [
        {
            "type":   r["emergency_type"],
            "icon":   ICONS.get(r["emergency_type"], "🆘"),
            "action": r["action"],
            "lang":   r["language"],
            "created_at": (r["created_at"].isoformat() + "Z") if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        }
        for r in rows
    ]
    return jsonify({"success": True, "history": history})


@history_bp.route("/clear", methods=["DELETE"])
@login_required
def clear_history():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM history WHERE user_id = %s", (session["user_id"],))
    db.commit()
    cursor.close()
    return jsonify({"success": True, "message": "History cleared."})
