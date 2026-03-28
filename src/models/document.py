"""문서 데이터 모델"""
from src.models.database import get_connection


class DocumentModel:
    @staticmethod
    def create(stage_id, name, template_type="", file_path="",
               status="Draft", reviewer="", notes="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO documents (stage_id, name, template_type, file_path, status, reviewer, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (stage_id, name, template_type, file_path, status, reviewer, notes)
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
    def get_next_id(stage_id, prefix="DOC", conn=None):
        """Generate next sequential ID like SWE1-REQ-001.

        Uses the stage's SWE level to determine the prefix:
        SWE.1->REQ, SWE.2->SAD, SWE.3->SDD, SWE.4->UT, SWE.5->IT, SWE.6->QT
        """
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        swe_prefix_map = {
            "SWE.1": "REQ",
            "SWE.2": "SAD",
            "SWE.3": "SDD",
            "SWE.4": "UT",
            "SWE.5": "IT",
            "SWE.6": "QT",
        }

        stage = conn.execute(
            "SELECT swe_level FROM stages WHERE id = ?", (stage_id,)
        ).fetchone()
        if stage:
            swe_level = stage["swe_level"]
            prefix = swe_prefix_map.get(swe_level, prefix)
            swe_num = swe_level.replace("SWE.", "")
        else:
            swe_num = "0"

        count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE stage_id = ?", (stage_id,)
        ).fetchone()[0]

        if should_close:
            conn.close()

        return f"SWE{swe_num}-{prefix}-{count + 1:03d}"

    @staticmethod
    def delete(doc_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        if should_close:
            conn.close()
