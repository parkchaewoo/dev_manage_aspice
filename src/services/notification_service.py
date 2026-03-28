"""마감일 알림 서비스"""
from datetime import date, timedelta

from src.models.database import get_connection


def check_overdue_milestones(conn=None):
    """완료되지 않은 기한 초과 마일스톤 조회"""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    today = date.today().isoformat()
    rows = conn.execute(
        """SELECT sm.*, p.name as project_name, s.swe_level
           FROM schedule_milestones sm
           JOIN projects p ON sm.project_id = p.id
           LEFT JOIN stages s ON sm.stage_id = s.id
           WHERE sm.due_date < ?
             AND sm.status != 'Completed'
           ORDER BY sm.due_date""",
        (today,)
    ).fetchall()

    if should_close:
        conn.close()
    return rows


def check_upcoming_deadlines(days=7, conn=None):
    """N일 내 마감 예정 마일스톤 조회"""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=days)).isoformat()
    rows = conn.execute(
        """SELECT sm.*, p.name as project_name, s.swe_level
           FROM schedule_milestones sm
           JOIN projects p ON sm.project_id = p.id
           LEFT JOIN stages s ON sm.stage_id = s.id
           WHERE sm.due_date >= ?
             AND sm.due_date <= ?
             AND sm.status != 'Completed'
           ORDER BY sm.due_date""",
        (today, future)
    ).fetchall()

    if should_close:
        conn.close()
    return rows


def get_notification_summary(conn=None):
    """모든 프로젝트의 기한 초과 + 다가오는 마감일 요약"""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    overdue = check_overdue_milestones(conn)
    upcoming = check_upcoming_deadlines(days=7, conn=conn)

    if should_close:
        conn.close()

    return {
        "overdue": overdue,
        "upcoming": upcoming,
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming),
        "total_count": len(overdue) + len(upcoming),
    }
