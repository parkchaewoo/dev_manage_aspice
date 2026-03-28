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

        CREATE TABLE IF NOT EXISTS phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            phase_order INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Active',
            inherited_from_phase_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (inherited_from_phase_id) REFERENCES phases(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS phase_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT DEFAULT '',
            entity_id INTEGER,
            description TEXT DEFAULT '',
            user_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            phase_id INTEGER,
            swe_level TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            planned_start DATE,
            planned_end DATE,
            actual_start DATE,
            actual_end DATE,
            notes TEXT DEFAULT '',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            template_type TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            content TEXT DEFAULT '',
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

    # === Migrations for existing DBs ===
    _run_migrations(conn)

    if should_close:
        conn.close()


def _run_migrations(conn):
    """기존 DB에 대한 스키마 마이그레이션"""
    migrations = [
        ("SELECT content FROM documents LIMIT 1",
         "ALTER TABLE documents ADD COLUMN content TEXT DEFAULT ''"),
        ("SELECT phase_id FROM stages LIMIT 1",
         "ALTER TABLE stages ADD COLUMN phase_id INTEGER"),
    ]
    for check_sql, alter_sql in migrations:
        try:
            conn.execute(check_sql)
        except Exception:
            try:
                conn.execute(alter_sql)
                conn.commit()
            except Exception:
                pass

    # Ensure phases and phase_logs tables exist (they're in CREATE IF NOT EXISTS, but just in case)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            phase_order INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Active',
            inherited_from_phase_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS phase_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT DEFAULT '',
            entity_id INTEGER,
            description TEXT DEFAULT '',
            user_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phase_id) REFERENCES phases(id) ON DELETE CASCADE
        );
    """)
    conn.commit()


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


def search_all(keyword, conn=None):
    """문서명, 체크리스트에서 키워드 검색"""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    results = []
    like = f"%{keyword}%"

    # 문서 검색
    docs = conn.execute(
        """SELECT d.id, d.name, d.status, s.swe_level, s.id as stage_id
           FROM documents d
           JOIN stages s ON d.stage_id = s.id
           WHERE d.name LIKE ?""", (like,)
    ).fetchall()
    for d in docs:
        results.append({
            "type": "document", "id": d["id"], "name": d["name"],
            "context": f"{d['swe_level']} | {d['status']}",
            "stage_id": d["stage_id"],
        })

    # 체크리스트 검색
    items = conn.execute(
        """SELECT c.id, c.description, c.is_checked, s.swe_level, s.id as stage_id
           FROM checklist_items c
           JOIN stages s ON c.stage_id = s.id
           WHERE c.description LIKE ?""", (like,)
    ).fetchall()
    for c in items:
        results.append({
            "type": "checklist", "id": c["id"], "name": c["description"],
            "context": f"{c['swe_level']} | {'Done' if c['is_checked'] else 'Pending'}",
            "stage_id": c["stage_id"],
        })

    if should_close:
        conn.close()
    return results
