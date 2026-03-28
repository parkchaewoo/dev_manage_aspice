"""일정 마일스톤 데이터 모델"""
from src.models.database import get_connection


class ScheduleModel:
    @staticmethod
    def create(project_id, name, due_date=None, stage_id=None,
               status="Pending", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO schedule_milestones (project_id, stage_id, name, due_date, status)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, stage_id, name, due_date, status)
        )
        conn.commit()
        mid = cursor.lastrowid
        if should_close:
            conn.close()
        return mid

    @staticmethod
    def get_by_project(project_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            """SELECT sm.*, s.swe_level
               FROM schedule_milestones sm
               LEFT JOIN stages s ON sm.stage_id = s.id
               WHERE sm.project_id = ?
               ORDER BY sm.due_date""",
            (project_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def update(milestone_id, **kwargs):
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
            values.append(milestone_id)
            conn.execute(
                f"UPDATE schedule_milestones SET {', '.join(fields)} WHERE id = ?", values
            )
            conn.commit()
        if should_close:
            conn.close()

    @staticmethod
    def delete(milestone_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM schedule_milestones WHERE id = ?", (milestone_id,))
        conn.commit()
        if should_close:
            conn.close()
