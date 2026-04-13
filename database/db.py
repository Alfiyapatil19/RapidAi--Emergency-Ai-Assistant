"""
RapidAid - Database Module
Uses PostgreSQL with psycopg2.
"""

import psycopg2
import psycopg2.extras
import os
from flask import g


def get_db():
    """Open a PostgreSQL database connection tied to the Flask request context."""
    if "db" not in g:
        # Check standard DATABASE_URL
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            # Fallback for local development if not provided or testing
            db_url = "postgresql://postgres:postgres@localhost:5432/rapidaid_db"
            print("Connecting to local fallback DB:", db_url)
            
        g.db = psycopg2.connect(
            db_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    return g.db


def close_db(e=None):
    """Close PostgreSQL connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from flask import current_app
    current_app.teardown_appcontext(close_db)

    # Note: On Render, the database is auto-created. 
    # But for initialization we run schema.sql to ensure tables exist.
    try:
        db     = get_db()
        cursor = db.cursor()

        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r") as f:
            sql = f.read()

        cursor.execute(sql)
        db.commit()
        cursor.close()
    except Exception as e:
        print(f"Warning: Database initialization failed. Check DATABASE_URL. ({e})")
