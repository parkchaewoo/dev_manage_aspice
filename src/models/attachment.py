"""첨부파일 데이터 모델"""
from src.models.database import get_connection


class AttachmentModel:
    @staticmethod
    def create(file_name, file_path, file_type="", description="",
               file_size=0, document_id=None, stage_id=None, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO attachments
               (file_name, file_path, file_type, description,
                file_size, document_id, stage_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_name, file_path, file_type, description,
             file_size, document_id, stage_id)
        )
        conn.commit()
        aid = cursor.lastrowid
        if should_close:
            conn.close()
        return aid

    @staticmethod
    def get_by_document(document_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM attachments WHERE document_id = ? ORDER BY created_at DESC",
            (document_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_stage(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM attachments WHERE stage_id = ? ORDER BY created_at DESC",
            (stage_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def delete(attachment_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        conn.commit()
        if should_close:
            conn.close()
