"""Database backup and restore service / 데이터베이스 백업 및 복원 서비스"""
import json
import os
import shutil

from src.models.database import DB_PATH, get_connection, initialize_schema


def backup_database(output_path):
    """Copy SQLite DB file to output_path."""
    if not os.path.isfile(DB_PATH):
        raise FileNotFoundError(f"Database file not found: {DB_PATH}")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    shutil.copy2(DB_PATH, output_path)
    return output_path


def restore_database(input_path):
    """Replace current DB with input file."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Backup file not found: {input_path}")
    # Validate that the input is a valid SQLite database
    import sqlite3
    try:
        test_conn = sqlite3.connect(input_path)
        test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        test_conn.close()
    except sqlite3.DatabaseError:
        raise ValueError("The selected file is not a valid SQLite database.")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    shutil.copy2(input_path, DB_PATH)
    return DB_PATH


def export_to_json(output_path, conn=None):
    """Export all data as JSON."""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    tables = [
        "oems", "projects", "stages", "documents",
        "checklist_items", "traceability_links", "schedule_milestones",
    ]

    data = {}
    for table in tables:
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            data[table] = [dict(row) for row in rows]
        except Exception:
            data[table] = []

    if should_close:
        conn.close()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    return output_path


def import_from_json(input_path, conn=None):
    """Import data from JSON, replacing current data."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"JSON file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    should_close = conn is None
    if conn is None:
        conn = get_connection()

    # Order matters due to foreign keys - delete in reverse dependency order
    tables_ordered = [
        "schedule_milestones", "traceability_links", "checklist_items",
        "documents", "stages", "projects", "oems",
    ]

    # Disable foreign keys temporarily for the import
    conn.execute("PRAGMA foreign_keys = OFF")

    try:
        # Clear existing data
        for table in tables_ordered:
            conn.execute(f"DELETE FROM {table}")

        # Insert in dependency order (reverse of deletion order)
        for table in reversed(tables_ordered):
            rows = data.get(table, [])
            if not rows:
                continue
            columns = list(rows[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            col_names = ", ".join(columns)
            for row in rows:
                values = [row.get(c) for c in columns]
                conn.execute(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                    values,
                )

        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
    except Exception:
        conn.rollback()
        conn.execute("PRAGMA foreign_keys = ON")
        raise

    if should_close:
        conn.close()

    return input_path
