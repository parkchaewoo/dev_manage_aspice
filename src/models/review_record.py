"""리뷰 기록 데이터 모델"""
from src.models.database import get_connection


class ReviewRecordModel:
    @staticmethod
    def create(document_id, review_date, review_type="Formal", participants="",
               findings="", decisions="", action_items="", result="Open", notes="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO review_records
               (document_id, review_date, review_type, participants,
                findings, decisions, action_items, result, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (document_id, review_date, review_type, participants,
             findings, decisions, action_items, result, notes)
        )
        conn.commit()
        rid = cursor.lastrowid
        if should_close:
            conn.close()
        return rid

    @staticmethod
    def get_by_document(document_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM review_records WHERE document_id = ? ORDER BY review_date DESC",
            (document_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(record_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute(
            "SELECT * FROM review_records WHERE id = ?", (record_id,)
        ).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(record_id, **kwargs):
        conn = kwargs.pop('conn', None)
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        fields, values = [], []
        for key, val in kwargs.items():
            if val is not None:
                fields.append(f"{key} = ?")
                values.append(val)
        if fields:
            values.append(record_id)
            conn.execute(
                f"UPDATE review_records SET {', '.join(fields)} WHERE id = ?", values
            )
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(record_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM review_records WHERE id = ?", (record_id,))
        conn.commit()
        if should_close:
            conn.close()
