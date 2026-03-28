"""개발 단계(Phase) 데이터 모델"""
from src.models.database import get_connection


class PhaseModel:
    @staticmethod
    def create(project_id, name, description="", phase_order=1,
               inherited_from_phase_id=None, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO phases (project_id, name, description, phase_order, inherited_from_phase_id)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, name, description, phase_order, inherited_from_phase_id)
        )
        conn.commit()
        phase_id = cursor.lastrowid
        if should_close:
            conn.close()
        return phase_id

    @staticmethod
    def get_by_project(project_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM phases WHERE project_id = ? ORDER BY phase_order",
            (project_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(phase_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute(
            "SELECT * FROM phases WHERE id = ?", (phase_id,)
        ).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(phase_id, **kwargs):
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
            values.append(phase_id)
            conn.execute(
                f"UPDATE phases SET {', '.join(fields)} WHERE id = ?", values
            )
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(phase_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM phases WHERE id = ?", (phase_id,))
        conn.commit()
        if should_close:
            conn.close()
