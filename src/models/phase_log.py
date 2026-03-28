"""Phase 로그 데이터 모델"""
from src.models.database import get_connection


class PhaseLogModel:
    @staticmethod
    def create(phase_id, action, entity_type="", entity_id=None,
               description="", user_name="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO phase_logs (phase_id, action, entity_type, entity_id, description, user_name)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (phase_id, action, entity_type, entity_id, description, user_name)
        )
        conn.commit()
        log_id = cursor.lastrowid
        if should_close:
            conn.close()
        return log_id

    @staticmethod
    def get_by_phase(phase_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM phase_logs WHERE phase_id = ? ORDER BY created_at DESC",
            (phase_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows
