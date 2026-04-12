"""
RapidAid - Database Module
Uses MySQL with PyMySQL connector.
"""

import pymysql
import os
from flask import g


def get_db():
    """Open a MySQL database connection tied to the Flask request context."""
    if "db" not in g:
        g.db = pymysql.connect(
            host     = os.environ.get("MYSQL_HOST",     "localhost"),
            port     = int(os.environ.get("MYSQL_PORT", "3306")),
            user     = os.environ.get("MYSQL_USER",     "root"),
            password = os.environ.get("MYSQL_PASSWORD", ""),
            database = os.environ.get("MYSQL_DATABASE", "rapidaid_db"),
            cursorclass = pymysql.cursors.DictCursor,
            autocommit  = False,
            charset     = "utf8mb4",
        )
    return g.db


def close_db(e=None):
    """Close MySQL connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from flask import current_app
    current_app.teardown_appcontext(close_db)

    db     = get_db()
    cursor = db.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        sql = f.read()

    # Execute each statement separately
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for statement in statements:
        cursor.execute(statement)

    db.commit()
    cursor.close()
