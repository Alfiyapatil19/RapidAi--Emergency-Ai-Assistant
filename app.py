"""
RapidAid - Emergency First Aid Application
Main Flask Application Entry Point
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Import modules
from database.db import init_db, get_db
from routes.auth     import auth_bp
from routes.contacts import contacts_bp
from routes.firstaid import firstaid_bp
from routes.history  import history_bp
from routes.ai_guide import ai_bp
from routes.admin    import admin_bp

# App setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rapidaid-dev-secret-change-in-production")
app.permanent_session_lifetime = timedelta(days=7)
CORS(app)

# Register routes
app.register_blueprint(auth_bp,     url_prefix="/auth")
app.register_blueprint(contacts_bp, url_prefix="/contacts")
app.register_blueprint(firstaid_bp, url_prefix="/firstaid")
app.register_blueprint(history_bp,  url_prefix="/history")
app.register_blueprint(ai_bp,       url_prefix="/ai")
app.register_blueprint(admin_bp,    url_prefix="/admin")

# Initialize DB
with app.app_context():
    init_db()


# ============================================================
# HOME
# ============================================================
@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)


# ============================================================
# PANIC BUTTON (SEND SMS)
# ============================================================
@app.route("/panic", methods=["POST"])
def panic():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Login required."}), 401

    data          = request.get_json() or {}
    user_location = data.get("location", "Unknown Location")

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name, phone FROM contacts WHERE user_id = %s", (session["user_id"],))
    contacts = cursor.fetchall()

    if not contacts:
        cursor.close()
        return jsonify({"success": False, "message": "No contacts found.", "alerted": []}), 400

    contact_list = [{"name": c["name"], "phone": c["phone"]} for c in contacts]
    sender_name  = session.get("user", "RapidAid User")

    # 🔥 SMS SERVICE (Twilio)
    from services.sms import send_panic_sms
    sms_result = send_panic_sms(contact_list, sender_name, user_location)

    logger.info(f"Panic SMS result: {sms_result}")

    status_msg = "SMS sent" if sms_result.get("success") else "SMS failed"

    cursor.execute(
        "INSERT INTO history (user_id, emergency_type, action, language) VALUES (%s, %s, %s, %s)",
        (session["user_id"], "PANIC_MODE", f"Panic triggered — {status_msg}", "en")
    )
    db.commit()
    cursor.close()

    return jsonify({
        "success": sms_result.get("success", False),
        "message": sms_result.get("message", ""),
        "alerted": contact_list,
        "count": len(contact_list),
        "sms_results": sms_result.get("results", [])
    })


# ============================================================
# STATUS CHECK
# ============================================================
@app.route("/status")
def status():
    return jsonify({
        "status": "ok",
        "features": {
            "sms": bool(os.environ.get("TWILIO_ACCOUNT_SID")),
            "ai":  bool(os.environ.get("HF_TOKEN")),
            "db":  True,
        },
        "sms_provider": "Twilio",
        "ai_provider":  "Hugging Face",
    })


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return render_template("500.html"), 500


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("RapidAid starting...")
    logger.info(f"SMS (Twilio): {'✅ Configured' if os.environ.get('TWILIO_ACCOUNT_SID') else '⚠️ Not configured'}")
    logger.info(f"AI (Hugging Face): {'✅ Configured' if os.environ.get('HF_TOKEN') else '⚠️ Not configured'}")
    logger.info("Admin Panel: http://127.0.0.1:5000/admin")
    logger.info("=" * 60)

    app.run(debug=True, host="0.0.0.0", port=5000)