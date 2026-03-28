"""프로젝트 데이터 모델"""
from src.models.database import get_connection


class ProjectModel:
    @staticmethod
    def create(oem_id, name, description="", status="Active",
               start_date=None, target_end_date=None, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO projects (oem_id, name, description, status, start_date, target_end_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (oem_id, name, description, status, start_date, target_end_date)
        )
        conn.commit()
        pid = cursor.lastrowid
        if should_close:
            conn.close()
        return pid

    @staticmethod
    def get_all(conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT p.*, o.name as oem_name FROM projects p JOIN oems o ON p.oem_id = o.id ORDER BY o.name, p.name"
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_oem(oem_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM projects WHERE oem_id = ? ORDER BY name", (oem_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_by_id(project_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def update(project_id, **kwargs):
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
            values.append(project_id)
            conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(project_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        if should_close:
            conn.close()
