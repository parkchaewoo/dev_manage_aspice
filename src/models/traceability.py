"""추적성 링크 데이터 모델"""
from src.models.database import get_connection


class TraceabilityModel:
    @staticmethod
    def create(source_document_id, target_document_id, link_type="derives",
               description="", source_item_id="", target_item_id="", conn=None):
        should_close = conn is None
        if conn is None:
            conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO traceability_links
               (source_document_id, target_document_id, link_type, description,
                source_item_id, target_item_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (source_document_id, target_document_id, link_type, description,
             source_item_id, target_item_id)
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
        """두 단계 간 추적성 완성도 계산 (아이템 단위)"""
        import json
        should_close = conn is None
        if conn is None:
            conn = get_connection()

        # 각 단계의 아이템 수 (문서 content JSON 파싱)
        def _count_items(stage_id):
            docs = conn.execute(
                "SELECT content FROM documents WHERE stage_id = ?", (stage_id,)
            ).fetchall()
            total = 0
            for doc in docs:
                try:
                    content = doc["content"] or ""
                    items = json.loads(content)
                    if isinstance(items, list):
                        total += len(items)
                except (json.JSONDecodeError, TypeError, IndexError, KeyError):
                    pass
            return max(total, 1)  # 최소 1 (0으로 나누기 방지)

        items_1 = _count_items(stage_id_1)
        items_2 = _count_items(stage_id_2)

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

        # 링크된 고유 아이템 ID 수 (소스 측 기준)
        link_rows = conn.execute(
            """SELECT tl.source_item_id, tl.target_item_id
               FROM traceability_links tl
               JOIN documents sd ON tl.source_document_id = sd.id
               JOIN documents td ON tl.target_document_id = td.id
               WHERE (sd.stage_id = ? AND td.stage_id = ?)
                  OR (sd.stage_id = ? AND td.stage_id = ?)""",
            (stage_id_1, stage_id_2, stage_id_2, stage_id_1)
        ).fetchall()

        linked_item_ids = set()
        for row in link_rows:
            try:
                src = row["source_item_id"]
                tgt = row["target_item_id"]
                if src:
                    linked_item_ids.add(src)
                if tgt:
                    linked_item_ids.add(tgt)
            except (IndexError, KeyError):
                pass

        # 커버리지 계산
        has_item_ids = any(
            row["source_item_id"] for row in link_rows
            if row["source_item_id"]
        ) if link_rows else False

        if has_item_ids:
            # 아이템 단위: 소스 아이템 중 링크된 비율
            source_linked = set()
            for row in link_rows:
                try:
                    src = row["source_item_id"]
                    if src:
                        source_linked.add(src)
                except (IndexError, KeyError):
                    pass
            pct = (len(source_linked) / items_1 * 100) if items_1 > 0 else 0
        else:
            # 레거시 (문서 단위): 링크 존재 여부로 판단
            pct = 100.0 if links > 0 else 0.0

        pct = min(pct, 100)

        if should_close:
            conn.close()
        return {
            "items_stage_1": items_1,
            "items_stage_2": items_2,
            "link_count": links,
            "linked_items": len(linked_item_ids),
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
