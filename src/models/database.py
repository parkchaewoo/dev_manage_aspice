"""SQLite 데이터베이스 관리"""
import os
import sqlite3


DB_PATH = os.path.join(os.path.expanduser("~"), ".aspice_manager", "aspice_manager.db")


def get_connection(db_path=None):
    """SQLite 연결 반환"""
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_schema(conn=None):
    """전체 스키마 생성"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS oems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            config_yaml TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oem_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'Active',
            start_date DATE,
            target_end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (oem_id) REFERENCES oems(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            swe_level TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            planned_start DATE,
            planned_end DATE,
            actual_start DATE,
            actual_end DATE,
            notes TEXT DEFAULT '',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            template_type TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            status TEXT DEFAULT 'Draft',
            reviewer TEXT DEFAULT '',
            review_date DATE,
            approval_date DATE,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stage_id) REFERENCES stages(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS checklist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            is_checked INTEGER DEFAULT 0,
            checked_by TEXT DEFAULT '',
            checked_at TIMESTAMP,
            FOREIGN KEY (stage_id) REFERENCES stages(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS traceability_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_document_id INTEGER NOT NULL,
            target_document_id INTEGER NOT NULL,
            link_type TEXT DEFAULT 'derives',
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_document_id) REFERENCES documents(id) ON DELETE CASCADE,
            FOREIGN KEY (target_document_id) REFERENCES documents(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS schedule_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            stage_id INTEGER,
            name TEXT NOT NULL,
            due_date DATE,
            completed_date DATE,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (stage_id) REFERENCES stages(id) ON DELETE SET NULL
        );
    """)
    conn.commit()

    if should_close:
        conn.close()


def is_db_initialized(conn=None):
    """DB에 데이터가 있는지 확인"""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cursor = conn.execute("SELECT COUNT(*) FROM oems")
    count = cursor.fetchone()[0]

    if should_close:
        conn.close()
    return count > 0
