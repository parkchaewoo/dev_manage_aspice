"""시험 결과 데이터 모델"""
from src.models.database import get_connection


class TestResultModel:
    @staticmethod
    def create(stage_id, test_date=None, test_type="", total_cases=0,
               passed=0, failed=0, blocked=0, not_executed=0, pass_rate=0,
               coverage_statement=0, coverage_branch=0, coverage_mcdc=0,
               tool_name="", tool_version="", notes="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO test_results
               (stage_id, test_date, test_type, total_cases,
                passed, failed, blocked, not_executed, pass_rate,
                coverage_statement, coverage_branch, coverage_mcdc,
                tool_name, tool_version, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (stage_id, test_date, test_type, total_cases,
             passed, failed, blocked, not_executed, pass_rate,
             coverage_statement, coverage_branch, coverage_mcdc,
             tool_name, tool_version, notes)
        )
        conn.commit()
        rid = cursor.lastrowid
        if should_close:
            conn.close()
        return rid

    @staticmethod
    def get_by_stage(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM test_results WHERE stage_id = ? ORDER BY test_date DESC",
            (stage_id,)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_latest_by_stage(stage_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        row = conn.execute(
            "SELECT * FROM test_results WHERE stage_id = ? ORDER BY test_date DESC LIMIT 1",
            (stage_id,)
        ).fetchone()
        if should_close:
            conn.close()
        return row

    @staticmethod
    def delete(result_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM test_results WHERE id = ?", (result_id,))
        conn.commit()
        if should_close:
            conn.close()
