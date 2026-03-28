"""추적성 링크 데이터 모델"""
from src.models.database import get_connection


class TraceabilityModel:
    @staticmethod
    def create(source_document_id, target_document_id, link_type="derives",
               description="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO traceability_links
               (source_document_id, target_document_id, link_type, description)
               VALUES (?, ?, ?, ?)""",
            (source_document_id, target_document_id, link_type, description)
        )
        conn.commit()
        lid = cursor.lastrowid
        if should_close:
            conn.close()
        return lid

    @staticmethod
    def get_by_document(doc_id, conn=None):
        """문서에 연결된 모든 추적성 링크 조회"""
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            """SELECT tl.*,
                      sd.name as source_name, sd.status as source_status,
                      td.name as target_name, td.status as target_status
               FROM traceability_links tl
               JOIN documents sd ON tl.source_document_id = sd.id
               JOIN documents td ON tl.target_document_id = td.id
               WHERE tl.source_document_id = ? OR tl.target_document_id = ?""",
            (doc_id, doc_id)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_between_stages(stage_id_1, stage_id_2, conn=None):
        """두 단계 사이의 모든 추적성 링크 조회"""
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        rows = conn.execute(
            """SELECT tl.*,
                      sd.name as source_name, sd.status as source_status,
                      sd.stage_id as source_stage_id,
                      td.name as target_name, td.status as target_status,
                      td.stage_id as target_stage_id
               FROM traceability_links tl
               JOIN documents sd ON tl.source_document_id = sd.id
               JOIN documents td ON tl.target_document_id = td.id
               WHERE (sd.stage_id = ? AND td.stage_id = ?)
                  OR (sd.stage_id = ? AND td.stage_id = ?)""",
            (stage_id_1, stage_id_2, stage_id_2, stage_id_1)
        ).fetchall()
        if should_close:
            conn.close()
        return rows

    @staticmethod
    def get_completeness_for_pair(stage_id_1, stage_id_2, conn=None):
        """두 단계 간 추적성 완성도 계산"""
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        # 각 단계의 문서 수
        docs_1 = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE stage_id = ?", (stage_id_1,)
        ).fetchone()[0]
        docs_2 = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE stage_id = ?", (stage_id_2,)
        ).fetchone()[0]
        # 연결된 링크 수
        links = conn.execute(
            """SELECT COUNT(DISTINCT tl.id)
               FROM traceability_links tl
               JOIN documents sd ON tl.source_document_id = sd.id
               JOIN documents td ON tl.target_document_id = td.id
               WHERE (sd.stage_id = ? AND td.stage_id = ?)
                  OR (sd.stage_id = ? AND td.stage_id = ?)""",
            (stage_id_1, stage_id_2, stage_id_2, stage_id_1)
        ).fetchone()[0]
        # 링크가 있는 고유 문서 수
        linked_docs = conn.execute(
            """SELECT COUNT(DISTINCT doc_id) FROM (
                SELECT sd.id as doc_id FROM traceability_links tl
                JOIN documents sd ON tl.source_document_id = sd.id
                JOIN documents td ON tl.target_document_id = td.id
                WHERE (sd.stage_id = ? AND td.stage_id = ?)
                   OR (sd.stage_id = ? AND td.stage_id = ?)
                UNION
                SELECT td.id FROM traceability_links tl
                JOIN documents sd ON tl.source_document_id = sd.id
                JOIN documents td ON tl.target_document_id = td.id
                WHERE (sd.stage_id = ? AND td.stage_id = ?)
                   OR (sd.stage_id = ? AND td.stage_id = ?)
            )""",
            (stage_id_1, stage_id_2, stage_id_2, stage_id_1,
             stage_id_1, stage_id_2, stage_id_2, stage_id_1)
        ).fetchone()[0]

        total_docs = docs_1 + docs_2
        pct = (linked_docs / total_docs * 100) if total_docs > 0 else 0

        if should_close:
            conn.close()
        return {
            "docs_stage_1": docs_1,
            "docs_stage_2": docs_2,
            "link_count": links,
            "linked_docs": linked_docs,
            "total_docs": total_docs,
            "completeness_pct": pct,
        }

    @staticmethod
    def delete(link_id, conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        conn.execute("DELETE FROM traceability_links WHERE id = ?", (link_id,))
        conn.commit()
        if should_close:
            conn.close()
