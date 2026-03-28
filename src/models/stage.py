"""SWE 단계 데이터 모델"""
from src.models.database import get_connection


class StageModel:
    @staticmethod
    def create(project_id, swe_level, status="Not Started",
               planned_start=None, planned_end=None, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO stages (project_id, swe_level, status, planned_start, planned_end)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, swe_level, status, planned_start, planned_end)
        )
        conn.commit()
        sid = cursor.lastrowid
        if should_close:
            conn.close()
        return sid

    @staticmethod
    def get_by_project(project_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM stages WHERE project_id = ? ORDER BY swe_level", (project_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute("SELECT * FROM stages WHERE id = ?", (stage_id,)).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(stage_id, **kwargs):
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
            values.append(stage_id)
            conn.execute(f"UPDATE stages SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def get_completion_stats(stage_id, conn=None):
        """체크리스트 및 문서 기반 완료율 계산"""
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        # 체크리스트 진행률
        total = conn.execute(
            "SELECT COUNT(*) FROM checklist_items WHERE stage_id = ?", (stage_id,)
        ).fetchone()[0]
        checked = conn.execute(
            "SELECT COUNT(*) FROM checklist_items WHERE stage_id = ? AND is_checked = 1", (stage_id,)
        ).fetchone()[0]
        # 문서 승인률
        doc_total = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE stage_id = ?", (stage_id,)
        ).fetchone()[0]
        doc_approved = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE stage_id = ? AND status = 'Approved'", (stage_id,)
        ).fetchone()[0]
        if should_close:
            conn.close()
        checklist_pct = (checked / total * 100) if total > 0 else 0
        doc_pct = (doc_approved / doc_total * 100) if doc_total > 0 else 0
        return {
            "checklist_total": total,
            "checklist_checked": checked,
            "checklist_pct": checklist_pct,
            "doc_total": doc_total,
            "doc_approved": doc_approved,
            "doc_pct": doc_pct,
            "overall_pct": (checklist_pct + doc_pct) / 2 if (total > 0 or doc_total > 0) else 0,
        }
