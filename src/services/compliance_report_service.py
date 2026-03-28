"""ASPICE Compliance Report Service / ASPICE 준수 보고서 서비스

Generates a comprehensive HTML compliance evidence report covering
SWE stage analysis, V-Model traceability, and gap analysis.
"""
import json
import os
from datetime import datetime

from src.models.database import get_connection
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.models.phase import PhaseModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel
from src.utils.constants import (
    SWE_STAGES, VMODEL_PAIRS, SEQUENTIAL_PAIRS, STATUS_COLORS,
    APP_NAME, APP_VERSION_FILE,
)


def _read_version():
    """Read application version from VERSION file."""
    try:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(base, APP_VERSION_FILE), "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "0.1.0"


def _status_color(status):
    """Return hex color for a given status string."""
    return STATUS_COLORS.get(status, "#8E8E93")


def _risk_color(pct):
    """Return risk color based on percentage."""
    if pct >= 80:
        return "#34C759"  # Green
    elif pct >= 50:
        return "#FF9500"  # Yellow
    else:
        return "#FF3B30"  # Red


def _risk_label(pct):
    """Return risk label based on percentage."""
    if pct >= 80:
        return "Low / 낮음"
    elif pct >= 50:
        return "Medium / 중간"
    else:
        return "High / 높음"


def _readiness_level(pct):
    """Determine ASPICE readiness level."""
    if pct >= 90:
        return ("Ready / 준비 완료", "#34C759")
    elif pct >= 60:
        return ("Partially Ready / 부분적 준비", "#FF9500")
    else:
        return ("Not Ready / 준비 미완료", "#FF3B30")


def _severity(issue_type, value):
    """Determine gap severity."""
    if issue_type == "missing_docs":
        return ("Critical / 심각", "#FF3B30")
    elif issue_type == "incomplete_checklist":
        if value < 50:
            return ("Major / 중요", "#FF9500")
        return ("Minor / 경미", "#FF9500")
    elif issue_type == "low_traceability":
        if value < 50:
            return ("Critical / 심각", "#FF3B30")
        return ("Major / 중요", "#FF9500")
    return ("Minor / 경미", "#8E8E93")


def generate_compliance_report(project_id, phase_id=None, output_path=None, conn=None):
    """Generate ASPICE compliance evidence report as HTML.

    Args:
        project_id: ID of the project to report on.
        phase_id: Optional phase ID to scope the report.
        output_path: File path to write the HTML report. If None, returns HTML string.
        conn: Optional database connection.

    Returns:
        The generated HTML string.
    """
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    try:
        return _build_report(project_id, phase_id, output_path, conn)
    finally:
        if should_close:
            conn.close()


def _build_report(project_id, phase_id, output_path, conn):
    """Internal: assemble full report."""
    project = ProjectModel.get_by_id(project_id, conn=conn)
    if not project:
        raise ValueError(f"Project not found: {project_id}")

    oem = OemModel.get_by_id(project["oem_id"], conn=conn)
    oem_name = oem["name"] if oem else "N/A"

    phase = None
    phase_name = "All Phases / 전체 단계"
    if phase_id:
        phase = PhaseModel.get_by_id(phase_id, conn=conn)
        if phase:
            phase_name = phase["name"]

    # Gather stages
    if phase_id:
        stages = StageModel.get_by_phase(phase_id, conn=conn)
    else:
        stages = StageModel.get_by_project(project_id, conn=conn)

    # Build stage map: swe_level -> stage row
    stage_map = {}
    for s in stages:
        stage_map[s["swe_level"]] = s

    # Gather per-stage data
    stage_data = {}
    total_score = 0.0
    stage_count = 0
    total_docs = 0
    total_approved = 0
    total_pending = 0
    total_missing_stages = 0

    for swe_key in SWE_STAGES:
        stage = stage_map.get(swe_key)
        if not stage:
            stage_data[swe_key] = None
            continue

        stats = StageModel.get_completion_stats(stage["id"], conn=conn)
        docs = DocumentModel.get_by_stage(stage["id"], conn=conn)
        checklists = ChecklistModel.get_by_stage(stage["id"], conn=conn)

        approved = sum(1 for d in docs if d["status"] == "Approved")
        pending = sum(1 for d in docs if d["status"] in ("Draft", "In Review"))
        total_docs += len(docs)
        total_approved += approved
        total_pending += pending

        if len(docs) == 0:
            total_missing_stages += 1

        total_score += stats["overall_pct"]
        stage_count += 1

        stage_data[swe_key] = {
            "stage": stage,
            "stats": stats,
            "docs": docs,
            "checklists": checklists,
            "approved": approved,
            "pending": pending,
        }

    overall_pct = (total_score / stage_count) if stage_count > 0 else 0

    # V-model traceability data
    vmodel_data = {}
    for left, right in VMODEL_PAIRS.items():
        s1 = stage_map.get(left)
        s2 = stage_map.get(right)
        if s1 and s2:
            completeness = TraceabilityModel.get_completeness_for_pair(
                s1["id"], s2["id"], conn=conn
            )
            links = TraceabilityModel.get_between_stages(
                s1["id"], s2["id"], conn=conn
            )
            # Find unlinked docs
            docs_left = DocumentModel.get_by_stage(s1["id"], conn=conn)
            docs_right = DocumentModel.get_by_stage(s2["id"], conn=conn)
            linked_doc_ids = set()
            for lnk in links:
                linked_doc_ids.add(lnk["source_document_id"])
                linked_doc_ids.add(lnk["target_document_id"])

            unlinked_left = [d for d in docs_left if d["id"] not in linked_doc_ids]
            unlinked_right = [d for d in docs_right if d["id"] not in linked_doc_ids]

            vmodel_data[f"{left}-{right}"] = {
                "completeness": completeness,
                "links": links,
                "unlinked_left": unlinked_left,
                "unlinked_right": unlinked_right,
            }
        else:
            vmodel_data[f"{left}-{right}"] = None

    # Sequential traceability data (derives: SWE.1->2, SWE.2->3)
    sequential_data = {}
    for src_swe, tgt_swe in SEQUENTIAL_PAIRS.items():
        s1 = stage_map.get(src_swe)
        s2 = stage_map.get(tgt_swe)
        if s1 and s2:
            completeness = TraceabilityModel.get_completeness_for_pair(
                s1["id"], s2["id"], conn=conn
            )
            links = TraceabilityModel.get_between_stages(
                s1["id"], s2["id"], conn=conn
            )
            docs_src = DocumentModel.get_by_stage(s1["id"], conn=conn)
            docs_tgt = DocumentModel.get_by_stage(s2["id"], conn=conn)
            linked_doc_ids = set()
            for lnk in links:
                linked_doc_ids.add(lnk["source_document_id"])
                linked_doc_ids.add(lnk["target_document_id"])

            unlinked_src = [d for d in docs_src if d["id"] not in linked_doc_ids]
            unlinked_tgt = [d for d in docs_tgt if d["id"] not in linked_doc_ids]

            sequential_data[f"{src_swe}->{tgt_swe}"] = {
                "completeness": completeness,
                "links": links,
                "unlinked_src": unlinked_src,
                "unlinked_tgt": unlinked_tgt,
            }
        else:
            sequential_data[f"{src_swe}->{tgt_swe}"] = None

    # Gap analysis
    gaps = []
    for swe_key in SWE_STAGES:
        sd = stage_data.get(swe_key)
        if sd is None:
            gaps.append({
                "stage": swe_key,
                "issue": "Stage not configured / 단계 미설정",
                "severity": ("Critical / 심각", "#FF3B30"),
                "detail": "No stage record exists / 단계 레코드 없음",
            })
            continue
        if sd["stats"]["doc_total"] == 0:
            sev = _severity("missing_docs", 0)
            gaps.append({
                "stage": swe_key,
                "issue": "No documents / 문서 없음",
                "severity": sev,
                "detail": "0 documents registered / 등록된 문서 0건",
            })
        elif sd["approved"] == 0:
            sev = _severity("missing_docs", 0)
            gaps.append({
                "stage": swe_key,
                "issue": "No approved documents / 승인된 문서 없음",
                "severity": sev,
                "detail": f"{sd['stats']['doc_total']} docs, 0 approved / 승인 0건",
            })
        if sd["stats"]["checklist_total"] > 0 and sd["stats"]["checklist_pct"] < 100:
            sev = _severity("incomplete_checklist", sd["stats"]["checklist_pct"])
            gaps.append({
                "stage": swe_key,
                "issue": "Incomplete checklist / 체크리스트 미완료",
                "severity": sev,
                "detail": f"{sd['stats']['checklist_checked']}/{sd['stats']['checklist_total']} "
                          f"({sd['stats']['checklist_pct']:.0f}%)",
            })

    for pair_key, vd in vmodel_data.items():
        if vd is None:
            gaps.append({
                "stage": pair_key,
                "issue": "Traceability N/A / 추적성 해당없음",
                "severity": ("Major / 중요", "#FF9500"),
                "detail": "One or both stages missing / 단계 누락",
            })
        elif vd["completeness"]["completeness_pct"] < 100:
            sev = _severity("low_traceability", vd["completeness"]["completeness_pct"])
            gaps.append({
                "stage": pair_key,
                "issue": "Insufficient traceability / 추적성 부족",
                "severity": sev,
                "detail": f"{vd['completeness']['completeness_pct']:.0f}% coverage / 커버리지",
            })

    # Build HTML
    version = _read_version()
    gen_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_missing = total_docs - total_approved - total_pending
    if total_missing < 0:
        total_missing = 0

    html_parts = [
        _html_head(project["name"], version),
        _html_cover(project["name"], oem_name, phase_name, gen_date, version),
        _html_executive_summary(overall_pct, total_docs, total_approved, total_pending, total_missing),
        _html_vmodel_overview(stage_data),
        _html_swe_analysis(stage_data),
        _html_vmodel_traceability(vmodel_data, sequential_data),
        _html_gap_analysis(gaps),
        _html_conclusion(overall_pct, gaps),
        _html_footer(),
    ]
    html = "\n".join(html_parts)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

    return html


# ---------------------------------------------------------------------------
# HTML section builders
# ---------------------------------------------------------------------------

def _html_head(project_name, version):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASPICE Compliance Report - {_esc(project_name)}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: #1d1d1f;
    background: #f5f5f7;
    line-height: 1.6;
}}
.container {{
    max-width: 1000px;
    margin: 0 auto;
    padding: 40px 24px;
}}
h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
h2 {{
    font-size: 22px; font-weight: 600; margin: 32px 0 16px 0;
    padding-bottom: 8px; border-bottom: 2px solid #e5e5ea;
}}
h3 {{ font-size: 17px; font-weight: 600; margin: 20px 0 10px 0; }}
table {{
    width: 100%; border-collapse: collapse; margin: 12px 0 20px 0;
    background: #fff; border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
th, td {{
    padding: 10px 14px; text-align: left; font-size: 14px;
    border-bottom: 1px solid #f0f0f0;
}}
th {{
    background: #f9f9fb; font-weight: 600; color: #6e6e73;
    text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px;
}}
tr:last-child td {{ border-bottom: none; }}
.badge {{
    display: inline-block; padding: 3px 10px; border-radius: 12px;
    font-size: 12px; font-weight: 600; color: #fff;
}}
.cover {{
    text-align: center; padding: 60px 20px; margin-bottom: 40px;
    background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
    color: #fff; border-radius: 12px;
}}
.cover h1 {{ font-size: 32px; color: #fff; margin-bottom: 4px; }}
.cover .subtitle {{ font-size: 16px; opacity: 0.9; margin-bottom: 24px; }}
.cover .meta {{ font-size: 14px; opacity: 0.8; line-height: 1.8; }}
.summary-cards {{
    display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0;
}}
.card {{
    flex: 1; min-width: 200px; background: #fff; border-radius: 10px;
    padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    text-align: center;
}}
.card .value {{ font-size: 36px; font-weight: 700; }}
.card .label {{ font-size: 13px; color: #6e6e73; margin-top: 4px; }}
.progress-bar {{
    width: 100%; height: 8px; background: #e5e5ea; border-radius: 4px;
    overflow: hidden; margin: 6px 0;
}}
.progress-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
.check {{ color: #34C759; font-weight: bold; }}
.uncheck {{ color: #FF3B30; font-weight: bold; }}
.missing {{ background: #FFF0F0; }}
.section {{ margin-bottom: 32px; }}
.stage-box {{
    background: #fff; border-radius: 10px; padding: 20px; margin: 16px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}}
.conclusion-box {{
    background: #fff; border-radius: 10px; padding: 24px; margin: 16px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border-left: 4px solid;
}}
.recommendation {{ padding: 6px 0; padding-left: 20px; position: relative; }}
.recommendation::before {{ content: "\\25B6"; position: absolute; left: 0; color: #007AFF; font-size: 10px; top: 8px; }}
details {{ margin: 4px 0; }}
details summary {{ font-weight: 500; }}
.vmodel-summary {{ background: #f9f9fb; border-radius: 8px; padding: 16px; margin: 16px 0; }}
.vmodel-summary td {{ text-align: center; }}
.page-break {{ page-break-before: always; }}

@media print {{
    body {{ background: #fff; font-size: 12px; }}
    .container {{ padding: 20px; max-width: 100%; }}
    .cover {{ padding: 40px 20px; }}
    .card {{ box-shadow: none; border: 1px solid #e5e5ea; }}
    .stage-box {{ box-shadow: none; border: 1px solid #e5e5ea; }}
    table {{ box-shadow: none; border: 1px solid #e5e5ea; }}
    .conclusion-box {{ box-shadow: none; border: 1px solid #e5e5ea; }}
    h2 {{ page-break-after: avoid; }}
    table {{ page-break-inside: avoid; }}
    .page-break {{ page-break-before: always; }}
}}
</style>
</head>
<body>
<div class="container">
"""


def _html_cover(project_name, oem_name, phase_name, gen_date, version):
    return f"""
<!-- Cover Page / 표지 -->
<div class="cover">
    <h1>ASPICE Compliance Report</h1>
    <div class="subtitle">ASPICE 준수 보고서</div>
    <div class="meta">
        <strong>Project / 프로젝트:</strong> {_esc(project_name)}<br>
        <strong>OEM:</strong> {_esc(oem_name)}<br>
        <strong>Phase / 단계:</strong> {_esc(phase_name)}<br>
        <strong>Generated / 생성일:</strong> {gen_date}<br>
        <strong>{APP_NAME}:</strong> v{version}
    </div>
</div>
"""


def _html_executive_summary(overall_pct, total_docs, approved, pending, missing):
    risk_clr = _risk_color(overall_pct)
    risk_lbl = _risk_label(overall_pct)
    return f"""
<!-- Executive Summary / 요약 -->
<div class="section">
<h2>1. Executive Summary / 요약</h2>
<div class="summary-cards">
    <div class="card">
        <div class="value" style="color:{risk_clr}">{overall_pct:.1f}%</div>
        <div class="label">Overall Compliance / 전체 준수율</div>
        <div class="progress-bar"><div class="progress-fill" style="width:{overall_pct:.0f}%;background:{risk_clr}"></div></div>
    </div>
    <div class="card">
        <div class="value" style="color:#34C759">{approved}</div>
        <div class="label">Approved Docs / 승인 문서</div>
    </div>
    <div class="card">
        <div class="value" style="color:#FF9500">{pending}</div>
        <div class="label">Pending Docs / 대기 문서</div>
    </div>
    <div class="card">
        <div class="value" style="color:#FF3B30">{missing}</div>
        <div class="label">Rejected / Missing / 부적합</div>
    </div>
</div>
<table>
<tr><th>Metric / 항목</th><th>Value / 값</th></tr>
<tr><td>Total Documents / 전체 문서 수</td><td>{total_docs}</td></tr>
<tr><td>Approved / 승인</td><td>{approved}</td></tr>
<tr><td>Pending (Draft + In Review) / 대기</td><td>{pending}</td></tr>
<tr><td>Rejected or Missing / 부적합</td><td>{missing}</td></tr>
<tr><td>Risk Assessment / 리스크 평가</td>
    <td><span class="badge" style="background:{risk_clr}">{risk_lbl}</span></td></tr>
</table>
</div>
"""


def _render_content_preview(content, swe_key):
    """Render document content as HTML table if JSON items, or as text preview."""
    # Headers per SWE level for JSON items
    _ITEM_HEADERS = {
        "SWE.1": (["ID", "Requirement", "Priority", "Verification", "Notes"],
                   ["id", "requirement", "priority", "verification", "notes"]),
        "SWE.2": (["ID", "Component", "Responsibility", "Input", "Output", "Notes"],
                   ["id", "component", "responsibility", "input", "output", "notes"]),
        "SWE.3": (["ID", "Function", "Input", "Output", "Description", "Notes"],
                   ["id", "function", "input", "output", "description", "notes"]),
        "SWE.4": (["ID", "Function", "Test Desc", "Expected", "Actual", "Result", "Notes"],
                   ["id", "function", "test_desc", "expected", "actual", "result", "notes"]),
        "SWE.5": (["ID", "Interface", "Test Desc", "Expected", "Actual", "Result", "Notes"],
                   ["id", "interface", "test_desc", "expected", "actual", "result", "notes"]),
        "SWE.6": (["ID", "Req ID", "Test Desc", "Expected", "Actual", "Result", "Notes"],
                   ["id", "req_id", "test_desc", "expected", "actual", "result", "notes"]),
    }
    try:
        items = json.loads(content)
        if isinstance(items, list) and items and isinstance(items[0], dict):
            headers_keys = _ITEM_HEADERS.get(swe_key)
            if headers_keys:
                headers, keys = headers_keys
            else:
                keys = list(items[0].keys())
                headers = [k.replace("_", " ").title() for k in keys]

            parts = ['<table style="font-size:12px;margin:8px 0">']
            parts.append('<tr>' + ''.join(f'<th>{_esc(h)}</th>' for h in headers) + '</tr>')
            for item in items:
                parts.append('<tr>' + ''.join(
                    f'<td>{_esc(str(item.get(k, "")))}</td>' for k in keys
                ) + '</tr>')
            parts.append('</table>')
            return '\n'.join(parts)
    except (json.JSONDecodeError, TypeError):
        pass

    # Legacy text content fallback
    preview = content[:500]
    return (f'<pre style="background:#f9f9fb;padding:10px;border-radius:6px;'
            f'font-size:12px;white-space:pre-wrap;max-height:200px;overflow:auto">'
            f'{_esc(preview)}{"..." if len(content) > 500 else ""}</pre>')


def _svg_vmodel(stage_data):
    """Generate an inline SVG V-Model diagram (600x300px)."""
    import math
    positions = {
        "SWE.1": (30, 30),
        "SWE.6": (430, 30),
        "SWE.2": (110, 130),
        "SWE.5": (350, 130),
        "SWE.3": (190, 230),
        "SWE.4": (270, 230),
    }
    box_w, box_h = 120, 50

    status_colors = {
        "Completed": "#34C759",
        "In Progress": "#007AFF",
        "In Review": "#FF9500",
        "Not Started": "#8E8E93",
    }

    svg_parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" '
        'width="600" height="300" style="font-family:sans-serif;">'
    ]

    # Dashed lines for V-model pairs (SWE.1<->6, SWE.2<->5, SWE.3<->4)
    vmodel_pairs = [("SWE.1", "SWE.6"), ("SWE.2", "SWE.5"), ("SWE.3", "SWE.4")]
    for left, right in vmodel_pairs:
        lx, ly = positions[left]
        rx, ry = positions[right]
        svg_parts.append(
            f'<line x1="{lx + box_w}" y1="{ly + box_h // 2}" '
            f'x2="{rx}" y2="{ry + box_h // 2}" '
            f'stroke="#8E8E93" stroke-width="1.5" stroke-dasharray="6,4" />'
        )

    # Solid arrows for sequential flow (SWE.1->2->3 and SWE.4->5->6)
    seq_flow = [("SWE.1", "SWE.2"), ("SWE.2", "SWE.3"), ("SWE.3", "SWE.4"),
                ("SWE.4", "SWE.5"), ("SWE.5", "SWE.6")]
    for src, dst in seq_flow:
        sx, sy = positions[src]
        dx, dy = positions[dst]
        # Connect bottom-center of src to top-center of dst (for vertical flow)
        # or right-center to left-center for horizontal
        if sy < dy:
            # Going down
            x1, y1 = sx + box_w // 2, sy + box_h
            x2, y2 = dx + box_w // 2, dy
        elif sy > dy:
            # Going up
            x1, y1 = sx + box_w // 2, sy
            x2, y2 = dx + box_w // 2, dy + box_h
        else:
            # Same level (SWE.3 -> SWE.4)
            x1, y1 = sx + box_w, sy + box_h // 2
            x2, y2 = dx, dy + box_h // 2

        svg_parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#636366" stroke-width="1.5" />'
        )
        # Arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arr_len = 8
        ax1 = x2 - arr_len * math.cos(angle - 0.4)
        ay1 = y2 - arr_len * math.sin(angle - 0.4)
        ax2 = x2 - arr_len * math.cos(angle + 0.4)
        ay2 = y2 - arr_len * math.sin(angle + 0.4)
        svg_parts.append(
            f'<polygon points="{x2},{y2} {ax1:.1f},{ay1:.1f} {ax2:.1f},{ay2:.1f}" '
            f'fill="#636366" />'
        )

    # Draw boxes for each SWE stage
    for swe_key, (bx, by) in positions.items():
        sd = stage_data.get(swe_key)
        if sd is not None:
            status = sd["stage"]["status"]
        else:
            status = "Not Started"
        fill_color = status_colors.get(status, "#8E8E93")

        svg_parts.append(
            f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" rx="6" ry="6" '
            f'fill="{fill_color}" opacity="0.9" />'
        )
        # Stage label
        label = swe_key
        svg_parts.append(
            f'<text x="{bx + box_w // 2}" y="{by + 22}" text-anchor="middle" '
            f'fill="#fff" font-size="13" font-weight="bold">{_esc(label)}</text>'
        )
        # Status label
        svg_parts.append(
            f'<text x="{bx + box_w // 2}" y="{by + 39}" text-anchor="middle" '
            f'fill="#fff" font-size="10" opacity="0.9">{_esc(status)}</text>'
        )

    # Legend
    legend_y = 5
    for i, (label, color) in enumerate([
        ("Completed", "#34C759"), ("In Progress", "#007AFF"),
        ("In Review", "#FF9500"), ("Not Started", "#8E8E93")
    ]):
        lx = 10 + i * 140
        svg_parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="10" height="10" rx="2" fill="{color}" />'
        )
        svg_parts.append(
            f'<text x="{lx + 14}" y="{legend_y + 9}" fill="#6e6e73" font-size="9">{label}</text>'
        )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def _html_vmodel_overview(stage_data):
    """Generate V-Model Overview section with inline SVG diagram."""
    svg = _svg_vmodel(stage_data)
    return f"""
<!-- V-Model Overview / V-모델 개요 -->
<div class="section">
<h2>V-Model Overview / V-모델 개요</h2>
<div style="text-align:center;margin:16px 0;background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08)">
{svg}
</div>
<p style="color:#6e6e73;font-size:13px;text-align:center">
    Dashed lines: V-Model verification pairs / 점선: V-모델 검증 쌍 &nbsp;|&nbsp;
    Solid arrows: Sequential flow / 실선 화살표: 순차적 흐름
</p>
</div>
"""


def _html_swe_analysis(stage_data):
    parts = ["""
<!-- SWE Stage Analysis / SWE 단계 분석 -->
<div class="section page-break">
<h2>2. SWE Stage Analysis / SWE 단계 분석</h2>
"""]

    for swe_key, swe_info in SWE_STAGES.items():
        sd = stage_data.get(swe_key)
        parts.append(f'<div class="stage-box">')
        parts.append(f'<h3>{swe_key}: {swe_info["name_en"]} / {swe_info["name_ko"]}</h3>')

        if sd is None:
            parts.append('<p style="color:#FF3B30">Stage not configured / 단계 미설정</p>')
            parts.append('</div>')
            continue

        stage = sd["stage"]
        stats = sd["stats"]
        color = _status_color(stage["status"])

        # Stage overview
        parts.append(f"""
<table>
<tr><th>Attribute / 속성</th><th>Value / 값</th></tr>
<tr><td>Status / 상태</td><td><span class="badge" style="background:{color}">{_esc(stage["status"])}</span></td></tr>
<tr><td>Planned Start / 계획 시작일</td><td>{stage["planned_start"] or "N/A"}</td></tr>
<tr><td>Planned End / 계획 종료일</td><td>{stage["planned_end"] or "N/A"}</td></tr>
<tr><td>Completion / 완료율</td><td>
    <div class="progress-bar" style="display:inline-block;width:200px;vertical-align:middle">
        <div class="progress-fill" style="width:{stats['overall_pct']:.0f}%;background:{_risk_color(stats['overall_pct'])}"></div>
    </div> {stats['overall_pct']:.1f}%
</td></tr>
</table>
""")

        # Document list
        docs = sd["docs"]
        if docs:
            parts.append('<h3 style="margin-top:12px">Documents / 문서</h3>')
            parts.append('<table><tr><th>#</th><th>Name / 이름</th><th>Status / 상태</th>'
                         '<th>Reviewer / 검토자</th><th>Type / 유형</th><th>Reviews / 리뷰</th></tr>')
            for i, d in enumerate(docs, 1):
                dc = _status_color(d["status"])
                # Count review records (status transitions indicate reviews)
                review_count = 1 if d["status"] in ("In Review", "Approved", "Rejected") else 0
                parts.append(
                    f'<tr><td>{i}</td><td>{_esc(d["name"])}</td>'
                    f'<td><span class="badge" style="background:{dc}">{_esc(d["status"])}</span></td>'
                    f'<td>{_esc(d["reviewer"] or "-")}</td>'
                    f'<td>{_esc(d["template_type"] or "-")}</td>'
                    f'<td>{review_count}</td></tr>'
                )
            parts.append('</table>')

            # Document content previews (collapsible)
            for i, d in enumerate(docs, 1):
                try:
                    content = d["content"] or ""
                except (IndexError, KeyError):
                    content = ""
                parts.append(f'<details style="margin:4px 0 8px 0">')
                parts.append(f'<summary style="cursor:pointer;color:#007AFF;font-size:13px">'
                             f'{_esc(d["name"])} - Content Preview / 내용 미리보기</summary>')
                if content:
                    parts.append(_render_content_preview(content, swe_key))
                else:
                    parts.append('<p style="color:#8E8E93;font-size:13px;padding:8px">No content / 내용 없음</p>')
                parts.append('</details>')
        else:
            parts.append('<p style="color:#FF3B30;margin:8px 0">No documents registered / 등록된 문서 없음</p>')

        # Checklist
        checklists = sd["checklists"]
        if checklists:
            chk_pct = stats["checklist_pct"]
            parts.append(f'<h3 style="margin-top:12px">Checklist / 체크리스트 ({chk_pct:.0f}%)</h3>')
            parts.append('<table><tr><th>#</th><th>Item / 항목</th><th>Status</th><th>Checked By / 확인자</th></tr>')
            for i, c in enumerate(checklists, 1):
                if c["is_checked"]:
                    icon = '<span class="check">&#10003;</span>'
                else:
                    icon = '<span class="uncheck">&#10007;</span>'
                parts.append(
                    f'<tr><td>{i}</td><td>{_esc(c["description"])}</td>'
                    f'<td>{icon}</td>'
                    f'<td>{_esc(c["checked_by"] or "-")}</td></tr>'
                )
            parts.append('</table>')
        else:
            parts.append('<p style="color:#8E8E93;margin:8px 0">No checklist items / 체크리스트 항목 없음</p>')

        parts.append('</div>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_vmodel_traceability(vmodel_data, sequential_data=None):
    if sequential_data is None:
        sequential_data = {}

    parts = ["""
<!-- V-Model Traceability / V-모델 추적성 -->
<div class="section page-break">
<h2>3. V-Model Traceability Analysis / V-모델 추적성 분석</h2>
"""]

    # --- V-Model Pairs (verifies: left <-> right) ---
    parts.append('<h3>3.1 V-Model Pairs (Verifies) / V-모델 쌍 (검증)</h3>')

    for pair_key, vd in vmodel_data.items():
        left, right = pair_key.split("-")
        left_info = SWE_STAGES[left]
        right_info = SWE_STAGES[right]

        parts.append(f'<div class="stage-box">')
        parts.append(f'<h3>{left} ({left_info["name_en"]}) &#8596; {right} ({right_info["name_en"]})</h3>')
        parts.append(f'<p style="color:#6e6e73">{left_info["name_ko"]} &#8596; {right_info["name_ko"]}</p>')

        if vd is None:
            parts.append('<p style="color:#FF9500">One or both stages not available / 단계 미설정</p>')
            parts.append('</div>')
            continue

        comp = vd["completeness"]
        pct = comp["completeness_pct"]
        clr = _risk_color(pct)

        parts.append(f"""
<table>
<tr><th>Metric / 항목</th><th>Value / 값</th></tr>
<tr><td>Link Count / 링크 수</td><td>{comp['link_count']}</td></tr>
<tr><td>Coverage / 커버리지</td><td>
    <div class="progress-bar" style="display:inline-block;width:200px;vertical-align:middle">
        <div class="progress-fill" style="width:{pct:.0f}%;background:{clr}"></div>
    </div> {pct:.1f}%
</td></tr>
<tr><td>Docs in {left} / {left} 문서 수</td><td>{comp['docs_stage_1']}</td></tr>
<tr><td>Docs in {right} / {right} 문서 수</td><td>{comp['docs_stage_2']}</td></tr>
<tr><td>Linked Docs / 연결된 문서</td><td>{comp['linked_docs']}</td></tr>
</table>
""")

        # Linked documents table
        links = vd["links"]
        if links:
            parts.append('<h3 style="margin-top:8px">Linked Documents / 연결된 문서</h3>')
            parts.append('<table><tr><th>Source / 소스</th><th>&#8594;</th><th>Target / 대상</th><th>Type / 유형</th></tr>')
            for lnk in links:
                parts.append(
                    f'<tr><td>{_esc(lnk["source_name"])}</td>'
                    f'<td>&#8594;</td>'
                    f'<td>{_esc(lnk["target_name"])}</td>'
                    f'<td>{_esc(lnk["link_type"] if lnk["link_type"] else "")}</td></tr>'
                )
            parts.append('</table>')

        # Unlinked documents (highlighted in RED)
        unlinked_left = vd["unlinked_left"]
        unlinked_right = vd["unlinked_right"]
        if unlinked_left or unlinked_right:
            parts.append('<h3 style="margin-top:8px;color:#FF3B30">Unlinked Documents / 미연결 문서</h3>')
            parts.append('<table><tr><th>Stage / 단계</th><th>Document / 문서</th><th>Status / 상태</th></tr>')
            for d in unlinked_left:
                dc = _status_color(d["status"])
                parts.append(
                    f'<tr style="background:#FFF0F0"><td style="color:#FF3B30;font-weight:600">{left}</td>'
                    f'<td style="color:#FF3B30">{_esc(d["name"])}</td>'
                    f'<td><span class="badge" style="background:{dc}">{_esc(d["status"])}</span></td></tr>'
                )
            for d in unlinked_right:
                dc = _status_color(d["status"])
                parts.append(
                    f'<tr style="background:#FFF0F0"><td style="color:#FF3B30;font-weight:600">{right}</td>'
                    f'<td style="color:#FF3B30">{_esc(d["name"])}</td>'
                    f'<td><span class="badge" style="background:{dc}">{_esc(d["status"])}</span></td></tr>'
                )
            parts.append('</table>')

        parts.append('</div>')

    # --- Sequential Pairs (derives: SWE.1->2, SWE.2->3) ---
    if sequential_data:
        parts.append('<h3 style="margin-top:24px">3.2 Sequential Pairs (Derives) / 순차적 쌍 (도출)</h3>')

        for pair_key, sd in sequential_data.items():
            src_swe, tgt_swe = pair_key.split("->")
            src_info = SWE_STAGES[src_swe]
            tgt_info = SWE_STAGES[tgt_swe]

            parts.append(f'<div class="stage-box">')
            parts.append(f'<h3>{src_swe} ({src_info["name_en"]}) &#8594; {tgt_swe} ({tgt_info["name_en"]})</h3>')
            parts.append(f'<p style="color:#6e6e73">{src_info["name_ko"]} &#8594; {tgt_info["name_ko"]}</p>')

            if sd is None:
                parts.append('<p style="color:#FF9500">One or both stages not available / 단계 미설정</p>')
                parts.append('</div>')
                continue

            comp = sd["completeness"]
            pct = comp["completeness_pct"]
            clr = _risk_color(pct)

            parts.append(f"""
<table>
<tr><th>Metric / 항목</th><th>Value / 값</th></tr>
<tr><td>Link Count / 링크 수</td><td>{comp['link_count']}</td></tr>
<tr><td>Coverage / 커버리지</td><td>
    <div class="progress-bar" style="display:inline-block;width:200px;vertical-align:middle">
        <div class="progress-fill" style="width:{pct:.0f}%;background:{clr}"></div>
    </div> {pct:.1f}%
</td></tr>
</table>
""")

            links = sd["links"]
            if links:
                parts.append('<table><tr><th>Source / 소스</th><th>&#8594;</th><th>Target / 대상</th><th>Type / 유형</th></tr>')
                for lnk in links:
                    parts.append(
                        f'<tr><td>{_esc(lnk["source_name"])}</td>'
                        f'<td>&#8594;</td>'
                        f'<td>{_esc(lnk["target_name"])}</td>'
                        f'<td>{_esc(lnk["link_type"] if lnk["link_type"] else "derives")}</td></tr>'
                    )
                parts.append('</table>')

            # Unlinked docs in sequential pairs
            unlinked_src = sd.get("unlinked_src", [])
            unlinked_tgt = sd.get("unlinked_tgt", [])
            if unlinked_src or unlinked_tgt:
                parts.append('<h3 style="margin-top:8px;color:#FF3B30">Unlinked Documents / 미연결 문서</h3>')
                parts.append('<table><tr><th>Stage / 단계</th><th>Document / 문서</th><th>Status / 상태</th></tr>')
                for d in unlinked_src:
                    dc = _status_color(d["status"])
                    parts.append(
                        f'<tr style="background:#FFF0F0"><td style="color:#FF3B30;font-weight:600">{src_swe}</td>'
                        f'<td style="color:#FF3B30">{_esc(d["name"])}</td>'
                        f'<td><span class="badge" style="background:{dc}">{_esc(d["status"])}</span></td></tr>'
                    )
                for d in unlinked_tgt:
                    dc = _status_color(d["status"])
                    parts.append(
                        f'<tr style="background:#FFF0F0"><td style="color:#FF3B30;font-weight:600">{tgt_swe}</td>'
                        f'<td style="color:#FF3B30">{_esc(d["name"])}</td>'
                        f'<td><span class="badge" style="background:{dc}">{_esc(d["status"])}</span></td></tr>'
                    )
                parts.append('</table>')

            parts.append('</div>')

    # --- V-Model Summary Table ---
    parts.append('<h3 style="margin-top:24px">3.3 V-Model Summary / V-모델 요약</h3>')
    parts.append('<div class="vmodel-summary">')
    parts.append('<table>')
    parts.append('<tr><th>Pair / 쌍</th><th>Type / 유형</th><th>Links / 링크</th>'
                 '<th>Coverage / 커버리지</th><th>Status / 상태</th></tr>')

    # V-model pairs summary
    for pair_key, vd in vmodel_data.items():
        left, right = pair_key.split("-")
        if vd is None:
            parts.append(
                f'<tr><td>{left} &#8596; {right}</td><td>verifies</td>'
                f'<td>-</td><td>-</td>'
                f'<td><span class="badge" style="background:#FF9500">N/A</span></td></tr>'
            )
        else:
            comp = vd["completeness"]
            pct = comp["completeness_pct"]
            clr = _risk_color(pct)
            parts.append(
                f'<tr><td>{left} &#8596; {right}</td><td>verifies</td>'
                f'<td>{comp["link_count"]}</td>'
                f'<td><span style="color:{clr};font-weight:600">{pct:.1f}%</span></td>'
                f'<td><span class="badge" style="background:{clr}">'
                f'{"OK" if pct >= 80 else "Gap"}</span></td></tr>'
            )

    # Sequential pairs summary
    for pair_key, sd in sequential_data.items():
        src_swe, tgt_swe = pair_key.split("->")
        if sd is None:
            parts.append(
                f'<tr><td>{src_swe} &#8594; {tgt_swe}</td><td>derives</td>'
                f'<td>-</td><td>-</td>'
                f'<td><span class="badge" style="background:#FF9500">N/A</span></td></tr>'
            )
        else:
            comp = sd["completeness"]
            pct = comp["completeness_pct"]
            clr = _risk_color(pct)
            parts.append(
                f'<tr><td>{src_swe} &#8594; {tgt_swe}</td><td>derives</td>'
                f'<td>{comp["link_count"]}</td>'
                f'<td><span style="color:{clr};font-weight:600">{pct:.1f}%</span></td>'
                f'<td><span class="badge" style="background:{clr}">'
                f'{"OK" if pct >= 80 else "Gap"}</span></td></tr>'
            )

    parts.append('</table>')
    parts.append('</div>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_gap_analysis(gaps):
    parts = ["""
<!-- Gap Analysis / 갭 분석 -->
<div class="section page-break">
<h2>4. Gap Analysis / 갭 분석</h2>
"""]

    if not gaps:
        parts.append('<p style="color:#34C759;font-weight:600">No gaps identified. '
                      'All criteria are met. / 식별된 갭 없음. 모든 기준 충족.</p>')
    else:
        parts.append(f'<p>Total issues identified / 식별된 이슈: <strong>{len(gaps)}</strong></p>')
        parts.append('<table><tr><th>Stage / 단계</th><th>Issue / 이슈</th>'
                     '<th>Severity / 심각도</th><th>Detail / 상세</th></tr>')
        for g in gaps:
            sev_label, sev_color = g["severity"]
            parts.append(
                f'<tr><td>{_esc(g["stage"])}</td><td>{_esc(g["issue"])}</td>'
                f'<td><span class="badge" style="background:{sev_color}">{sev_label}</span></td>'
                f'<td>{_esc(g["detail"])}</td></tr>'
            )
        parts.append('</table>')

    parts.append('</div>')
    return "\n".join(parts)


def _html_conclusion(overall_pct, gaps):
    level_label, level_color = _readiness_level(overall_pct)

    critical_count = sum(1 for g in gaps if "Critical" in g["severity"][0])
    major_count = sum(1 for g in gaps if "Major" in g["severity"][0])
    minor_count = sum(1 for g in gaps if "Minor" in g["severity"][0])

    recommendations = []
    if critical_count > 0:
        recommendations.append(
            "Address all critical gaps immediately. Focus on missing documents "
            "and insufficient traceability. / 모든 심각 갭을 즉시 해결하세요. "
            "누락 문서 및 부족한 추적성에 집중하세요."
        )
    if major_count > 0:
        recommendations.append(
            "Complete pending checklists and improve traceability coverage. / "
            "대기 중인 체크리스트를 완료하고 추적성 커버리지를 개선하세요."
        )
    if overall_pct < 90:
        recommendations.append(
            "Review all document statuses and ensure approval workflow is followed. / "
            "모든 문서 상태를 검토하고 승인 워크플로우를 준수하세요."
        )
    if not recommendations:
        recommendations.append(
            "Maintain current compliance level and perform periodic reviews. / "
            "현재 준수 수준을 유지하고 정기 검토를 수행하세요."
        )

    rec_html = "\n".join(
        f'<div class="recommendation">{_esc(r)}</div>' for r in recommendations
    )

    return f"""
<!-- Conclusion / 결론 -->
<div class="section page-break">
<h2>5. Conclusion / 결론</h2>
<div class="conclusion-box" style="border-left-color:{level_color}">
    <h3>ASPICE Readiness Level / ASPICE 준비 수준</h3>
    <p style="font-size:24px;font-weight:700;color:{level_color};margin:8px 0">{level_label}</p>
    <p>Overall compliance: {overall_pct:.1f}% &mdash;
       Critical: {critical_count}, Major: {major_count}, Minor: {minor_count}</p>
</div>

<h3 style="margin-top:20px">Recommendations / 권고사항</h3>
<div style="margin:8px 0">
{rec_html}
</div>
</div>
"""


def _html_footer():
    return """
<div style="text-align:center;color:#8E8E93;font-size:12px;margin-top:40px;padding:20px 0;border-top:1px solid #e5e5ea">
    Generated by ASPICE Process Manager / ASPICE 프로세스 관리자에 의해 생성됨
</div>
</div><!-- end container -->
</body>
</html>
"""


def _esc(text):
    """Escape HTML special characters."""
    if text is None:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
