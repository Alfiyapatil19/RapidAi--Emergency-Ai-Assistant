"""
RapidAid - Emergency Contacts Routes
MySQL version — uses %s placeholders
"""

from flask import Blueprint, request, jsonify, session
from database.db import get_db

contacts_bp = Blueprint("contacts", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Login required."}), 401
        return f(*args, **kwargs)
    return decorated


@contacts_bp.route("/", methods=["GET"])
@login_required
def get_contacts():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, name, relation, phone, created_at FROM contacts WHERE user_id = %s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    rows = cursor.fetchall()
    cursor.close()
    return jsonify({"success": True, "contacts": rows})


@contacts_bp.route("/add", methods=["POST"])
@login_required
def add_contact():
    data     = request.get_json()
    name     = data.get("name", "").strip()
    relation = data.get("relation", "Contact").strip()
    phone    = data.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"success": False, "message": "Name and phone are required."}), 400

    db     = get_db()
    cursor = db.cursor()

    # Limit 10 contacts
    cursor.execute("SELECT COUNT(*) as cnt FROM contacts WHERE user_id = %s", (session["user_id"],))
    count = cursor.fetchone()["cnt"]
    if count >= 10:
        cursor.close()
        return jsonify({"success": False, "message": "Maximum 10 contacts allowed."}), 400

    cursor.execute(
        "INSERT INTO contacts (user_id, name, relation, phone) VALUES (%s, %s, %s, %s) RETURNING id",
        (session["user_id"], name, relation, phone)
    )
    new_id = cursor.fetchone()["id"]
    db.commit()
    cursor.close()

    return jsonify({"success": True, "message": "Contact added!", "id": new_id})


@contacts_bp.route("/delete/<int:contact_id>", methods=["DELETE"])
@login_required
def delete_contact(contact_id):
    db     = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT id FROM contacts WHERE id = %s AND user_id = %s",
        (contact_id, session["user_id"])
    )
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"success": False, "message": "Contact not found."}), 404

    cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
    db.commit()
    cursor.close()

    return jsonify({"success": True, "message": "Contact removed."})
