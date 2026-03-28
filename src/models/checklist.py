"""체크리스트 데이터 모델"""
from src.models.database import get_connection


class ChecklistModel:
    @staticmethod
    def create(stage_id, description, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO checklist_items (stage_id, description) VALUES (?, ?)",
            (stage_id, description)
        )
        conn.commit()
        cid = cursor.lastrowid
        if should_close:
            conn.close()
        return cid

    @staticmethod
    def get_by_stage(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM checklist_items WHERE stage_id = ? ORDER BY id", (stage_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def toggle(item_id, checked_by="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        item = conn.execute("SELECT is_checked FROM checklist_items WHERE id = ?", (item_id,)).fetchone()
        if item:
            new_val = 0 if item['is_checked'] else 1
            conn.execute(
                """UPDATE checklist_items
                   SET is_checked = ?, checked_by = ?,
                       checked_at = CASE WHEN ? = 1 THEN CURRENT_TIMESTAMP ELSE NULL END
                   WHERE id = ?""",
                (new_val, checked_by, new_val, item_id)
            )
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def exclude(item_id, reason="", conn=None):
        """체크리스트 항목 제외/제외 해제 토글"""
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        item = conn.execute("SELECT is_excluded FROM checklist_items WHERE id = ?", (item_id,)).fetchone()
        if item:
            new_val = 0 if item['is_excluded'] else 1
            conn.execute(
                "UPDATE checklist_items SET is_excluded = ?, exclude_reason = ? WHERE id = ?",
                (new_val, reason if new_val else "", item_id)
            )
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(item_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        conn.commit()
        if should_close:
            conn.close()
