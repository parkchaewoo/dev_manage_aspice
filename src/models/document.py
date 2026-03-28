"""문서 데이터 모델"""
from src.models.database import get_connection


class DocumentModel:
    @staticmethod
    def create(stage_id, name, template_type="", file_path="",
               status="Draft", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO documents (stage_id, name, template_type, file_path, status)
               VALUES (?, ?, ?, ?, ?)""",
            (stage_id, name, template_type, file_path, status)
        )
        conn.commit()
        did = cursor.lastrowid
        if should_close:
            conn.close()
        return did

    @staticmethod
    def get_by_stage(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM documents WHERE stage_id = ? ORDER BY name", (stage_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(doc_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(doc_id, **kwargs):
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
            values.append(doc_id)
            conn.execute(f"UPDATE documents SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(doc_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        if should_close:
            conn.close()
