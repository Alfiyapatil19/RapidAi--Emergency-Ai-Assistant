"""
RapidAid - Authentication Routes
MySQL version — uses %s placeholders
"""

from flask import Blueprint, request, jsonify, session
import bcrypt
from database.db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data     = request.get_json()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    db     = get_db()
    cursor = db.cursor()

    # Check duplicate email
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        return jsonify({"success": False, "message": "Email already registered."}), 409

    # Hash password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id",
        (name, email, hashed)
    )
    db.commit()
    user_id = cursor.fetchone()["id"]
    cursor.close()

    session.permanent = True
    session["user_id"] = user_id
    session["user"]    = name

    return jsonify({"success": True, "message": "Account created!", "name": name})


@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required."}), 400

    db     = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    session["user"]    = user["name"]

    return jsonify({"success": True, "message": "Logged in!", "name": user["name"]})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."})


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" in session:
        return jsonify({"logged_in": True, "name": session.get("user"), "id": session.get("user_id")})
    return jsonify({"logged_in": False})
