"""
RapidAid - Admin Panel Routes
Secure admin-only access to view users, contacts, history, panic logs.
Credentials set in .env file — no registration needed.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database.db import get_db
from functools import wraps
import os

admin_bp = Blueprint("admin", __name__)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


# ── ADMIN AUTH DECORATOR ──────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


# ── ADMIN LOGIN ───────────────────────────────────────────
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"]    = True
            session["admin_user"]  = username
            return redirect(url_for("admin.dashboard"))
        else:
            error = "Invalid username or password."
    return render_template("admin/login.html", error=error)


@admin_bp.route("/logout")
def logout():
    session.pop("is_admin", None)
    session.pop("admin_user", None)
    return redirect(url_for("admin.login"))


# ── ADMIN DASHBOARD ───────────────────────────────────────
@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM contacts")
    total_contacts = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM history")
    total_history = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM history WHERE emergency_type = 'PANIC_MODE'")
    total_panics = cursor.fetchone()["cnt"]

    # Recent 5 users
    cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY created_at DESC LIMIT 5")
    recent_users = cursor.fetchall()

    # Recent 5 panic events
    cursor.execute("""
        SELECT h.action, h.created_at, u.name as user_name
        FROM history h
        JOIN users u ON h.user_id = u.id
        WHERE h.emergency_type = 'PANIC_MODE'
        ORDER BY h.created_at DESC LIMIT 5
    """)
    recent_panics = cursor.fetchall()

    cursor.close()
    return render_template("admin/dashboard.html",
        total_users    = total_users,
        total_contacts = total_contacts,
        total_history  = total_history,
        total_panics   = total_panics,
        recent_users   = recent_users,
        recent_panics  = recent_panics,
    )


# ── ALL USERS ─────────────────────────────────────────────
@admin_bp.route("/users")
@admin_required
def users():
    db     = get_db()
    cursor = db.cursor()
    search = request.args.get("search", "").strip()

    if search:
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   COUNT(DISTINCT c.id) as contact_count,
                   COUNT(DISTINCT h.id) as history_count
            FROM users u
            LEFT JOIN contacts c ON c.user_id = u.id
            LEFT JOIN history  h ON h.user_id = u.id
            WHERE u.name LIKE %s OR u.email LIKE %s
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.created_at,
                   COUNT(DISTINCT c.id) as contact_count,
                   COUNT(DISTINCT h.id) as history_count
            FROM users u
            LEFT JOIN contacts c ON c.user_id = u.id
            LEFT JOIN history  h ON h.user_id = u.id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)

    all_users = cursor.fetchall()
    cursor.close()
    return render_template("admin/users.html", users=all_users, search=search)


# ── SINGLE USER DETAIL ────────────────────────────────────
@admin_bp.route("/users/<int:user_id>")
@admin_required
def user_detail(user_id):
    db     = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return redirect(url_for("admin.users"))

    cursor.execute("""
        SELECT name, relation, phone, created_at
        FROM contacts WHERE user_id = %s ORDER BY created_at DESC
    """, (user_id,))
    contacts = cursor.fetchall()

    cursor.execute("""
        SELECT emergency_type, action, language, created_at
        FROM history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50
    """, (user_id,))
    history = cursor.fetchall()

    cursor.close()
    return render_template("admin/user_detail.html",
        user     = user,
        contacts = contacts,
        history  = history,
    )


# ── DELETE USER ───────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    return redirect(url_for("admin.users"))


# ── PANIC LOGS ────────────────────────────────────────────
@admin_bp.route("/panic-logs")
@admin_required
def panic_logs():
    db     = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT h.action, h.created_at, h.language,
               u.name as user_name, u.email as user_email
        FROM history h
        JOIN users u ON h.user_id = u.id
        WHERE h.emergency_type = 'PANIC_MODE'
        ORDER BY h.created_at DESC
    """)
    logs = cursor.fetchall()
    cursor.close()
    return render_template("admin/panic_logs.html", logs=logs)
