"""Document and project export service / 문서 및 프로젝트 내보내기 서비스"""
import json
import os
from datetime import date

from src.models.database import get_connection
from src.models.document import DocumentModel
from src.models.stage import StageModel
from src.models.project import ProjectModel
from src.models.oem import OemModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel
from src.utils.constants import SWE_STAGES, VMODEL_PAIRS


# Map SWE level and template_type to template filename
_TEMPLATE_MAP = {
    "SWE.1": "SWE1_requirements_spec.md",
    "SWE.2": "SWE2_architecture_design.md",
    "SWE.3": "SWE3_detailed_design.md",
    "SWE.4": "SWE4_unit_test_report.md",
    "SWE.5": "SWE5_integration_test_report.md",
    "SWE.6": "SWE6_qualification_test_report.md",
    "srs": "SWE1_requirements_spec.md",
    "sad": "SWE2_architecture_design.md",
    "sdd": "SWE3_detailed_design.md",
    "ut_report": "SWE4_unit_test_report.md",
    "it_report": "SWE5_integration_test_report.md",
    "qt_report": "SWE6_qualification_test_report.md",
}

_TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")


def _get_template_content(swe_level):
    """Read template file for the given SWE level."""
    filename = _TEMPLATE_MAP.get(swe_level)
    if not filename:
        return None
    path = os.path.join(_TEMPLATES_DIR, filename)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _items_to_markdown(items, swe_level):
    """Convert JSON items to markdown table based on SWE level."""
    if not items:
        return ""

    # Define headers per SWE level
    headers_map = {
        "SWE.1": ["ID", "Requirement", "Priority", "Verification", "Notes"],
        "SWE.2": ["ID", "Component", "Responsibility", "Input", "Output", "Notes"],
        "SWE.3": ["ID", "Function", "Input", "Output", "Description", "Notes"],
        "SWE.4": ["ID", "Function", "Test Description", "Expected", "Actual", "Result", "Notes"],
        "SWE.5": ["ID", "Interface", "Test Description", "Expected", "Actual", "Result", "Notes"],
        "SWE.6": ["ID", "Req ID", "Test Description", "Expected", "Actual", "Result", "Notes"],
    }
    keys_map = {
        "SWE.1": ["id", "requirement", "priority", "verification", "notes"],
        "SWE.2": ["id", "component", "responsibility", "input", "output", "notes"],
        "SWE.3": ["id", "function", "input", "output", "description", "notes"],
        "SWE.4": ["id", "function", "test_desc", "expected", "actual", "result", "notes"],
        "SWE.5": ["id", "interface", "test_desc", "expected", "actual", "result", "notes"],
        "SWE.6": ["id", "req_id", "test_desc", "expected", "actual", "result", "notes"],
    }

    headers = headers_map.get(swe_level)
    keys = keys_map.get(swe_level)

    if not headers or not keys:
        # Fallback: use keys from first item
        keys = list(items[0].keys()) if items else []
        headers = [k.replace("_", " ").title() for k in keys]

    lines = []
    # Header row
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    # Data rows
    for item in items:
        row = [str(item.get(k, "")) for k in keys]
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def export_to_markdown(doc_id, output_path, conn=None):
    """Export document with template filled in as markdown file."""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    doc = DocumentModel.get_by_id(doc_id, conn)
    if not doc:
        if should_close:
            conn.close()
        raise ValueError(f"Document not found: {doc_id}")

    stage = StageModel.get_by_id(doc["stage_id"], conn)
    project = ProjectModel.get_by_id(stage["project_id"], conn)
    oem = OemModel.get_by_id(project["oem_id"], conn)

    if should_close:
        conn.close()

    swe_level = stage["swe_level"]

    # Build document header
    header = (
        f"# {project['name']} - {doc['name']}\n\n"
        f"| Field | Value |\n|---|---|\n"
        f"| OEM | {oem['name']} |\n"
        f"| Date | {date.today()} |\n"
        f"| Stage | {swe_level} |\n"
        f"| Status | {doc['status']} |\n\n"
        f"---\n\n"
    )

    # Handle document content - try JSON items first, fall back to plain text
    try:
        doc_content = doc["content"] or ""
    except (IndexError, KeyError):
        doc_content = ""
    content_body = ""

    try:
        items = json.loads(doc_content)
        if isinstance(items, list) and items:
            content_body = _items_to_markdown(items, swe_level)
    except (json.JSONDecodeError, TypeError):
        # Legacy plain text / markdown content - use as-is
        content_body = doc_content

    if not content_body:
        # Fall back to template if no content
        template = _get_template_content(swe_level)
        if template:
            content_body = template.replace("{project_name}", project["name"])
            content_body = content_body.replace("{oem_name}", oem["name"])
            content_body = content_body.replace("{date}", str(date.today()))
            content_body = content_body.replace("{document_id}", doc["name"])
            content_body = content_body.replace("{document_name}", doc["name"])
            content_body = content_body.replace("{status}", doc["status"])
            content_body = content_body.replace("{swe_level}", swe_level)

    content = header + content_body

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def export_to_html(doc_id, output_path, conn=None):
    """Convert markdown to basic HTML and save."""
    import re

    should_close = conn is None
    if conn is None:
        conn = get_connection()

    # First generate markdown content
    md_path = output_path + ".tmp.md"
    export_to_markdown(doc_id, md_path, conn)

    if should_close and conn:
        pass  # already closed in export_to_markdown

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    os.remove(md_path)

    # Simple markdown to HTML conversion
    html_lines = []
    in_table = False
    lines = md_content.split("\n")

    for line in lines:
        stripped = line.strip()

        # Headings
        if stripped.startswith("######"):
            html_lines.append(f"<h6>{stripped[6:].strip()}</h6>")
        elif stripped.startswith("#####"):
            html_lines.append(f"<h5>{stripped[5:].strip()}</h5>")
        elif stripped.startswith("####"):
            html_lines.append(f"<h4>{stripped[4:].strip()}</h4>")
        elif stripped.startswith("###"):
            html_lines.append(f"<h3>{stripped[3:].strip()}</h3>")
        elif stripped.startswith("##"):
            html_lines.append(f"<h2>{stripped[2:].strip()}</h2>")
        elif stripped.startswith("#"):
            html_lines.append(f"<h1>{stripped[1:].strip()}</h1>")
        elif stripped.startswith("---"):
            html_lines.append("<hr>")
        elif stripped.startswith("|"):
            # Table row
            if not in_table:
                html_lines.append("<table border='1' cellpadding='4' cellspacing='0'>")
                in_table = True
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            # Check if separator row
            if all(set(c) <= {"-", ":"} for c in cells):
                continue
            tag = "td"
            row_html = "<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>"
            html_lines.append(row_html)
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if stripped:
                # Bold
                processed = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
                html_lines.append(f"<p>{processed}</p>")
            else:
                html_lines.append("")

    if in_table:
        html_lines.append("</table>")

    html = (
        "<!DOCTYPE html>\n<html>\n<head>\n"
        "<meta charset='utf-8'>\n"
        "<style>\n"
        "body { font-family: Arial, sans-serif; margin: 20px; }\n"
        "table { border-collapse: collapse; width: 100%; margin: 10px 0; }\n"
        "td, th { border: 1px solid #ccc; padding: 6px 10px; }\n"
        "h1, h2, h3 { color: #333; }\n"
        "hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }\n"
        "</style>\n</head>\n<body>\n"
        + "\n".join(html_lines) +
        "\n</body>\n</html>"
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def export_project_report(project_id, output_path, conn=None):
    """Generate full project report with all stages summary."""
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    project = ProjectModel.get_by_id(project_id, conn)
    if not project:
        if should_close:
            conn.close()
        raise ValueError(f"Project not found: {project_id}")

    oem = OemModel.get_by_id(project["oem_id"], conn)
    stages = StageModel.get_by_project(project_id, conn)

    lines = [
        f"# Project Report: {project['name']}",
        f"# 프로젝트 리포트: {project['name']}",
        "",
        "---",
        "",
        "| Field / 항목 | Value / 값 |",
        "|---|---|",
        f"| Project / 프로젝트 | {project['name']} |",
        f"| OEM | {oem['name']} |",
        f"| Status / 상태 | {project['status']} |",
        f"| Start Date / 시작일 | {project['start_date'] or 'N/A'} |",
        f"| Target End Date / 목표 완료일 | {project['target_end_date'] or 'N/A'} |",
        f"| Report Date / 리포트 날짜 | {date.today()} |",
        "",
        "---",
        "",
        "## Stage Summary / 단계 요약",
        "",
        "| Stage / 단계 | Name / 이름 | Status / 상태 | Docs / 문서 | Checklist / 체크리스트 | Overall / 전체 |",
        "|---|---|---|---|---|---|",
    ]

    for stage in stages:
        swe = stage["swe_level"]
        swe_info = SWE_STAGES.get(swe, {})
        stats = StageModel.get_completion_stats(stage["id"], conn)
        lines.append(
            f"| {swe} | {swe_info.get('name_en', swe)} | {stage['status']} "
            f"| {stats['doc_approved']}/{stats['doc_total']} ({stats['doc_pct']:.0f}%) "
            f"| {stats['checklist_checked']}/{stats['checklist_total']} ({stats['checklist_pct']:.0f}%) "
            f"| {stats['overall_pct']:.0f}% |"
        )

    lines += ["", "---", ""]

    # Detail for each stage
    for stage in stages:
        swe = stage["swe_level"]
        swe_info = SWE_STAGES.get(swe, {})
        lines.append(f"## {swe}: {swe_info.get('name_en', swe)}")
        lines.append("")

        # Documents
        docs = DocumentModel.get_by_stage(stage["id"], conn)
        if docs:
            lines.append("### Documents / 문서")
            lines.append("")
            lines.append("| Name / 이름 | Status / 상태 | Reviewer / 검토자 |")
            lines.append("|---|---|---|")
            for doc in docs:
                lines.append(
                    f"| {doc['name']} | {doc['status']} | {doc['reviewer'] or '-'} |"
                )
            lines.append("")

        # Checklist
        items = ChecklistModel.get_by_stage(stage["id"], conn)
        if items:
            lines.append("### Checklist / 체크리스트")
            lines.append("")
            for item in items:
                check = "[x]" if item["is_checked"] else "[ ]"
                lines.append(f"- {check} {item['description']}")
            lines.append("")

        # Traceability stats for V-model pairs
        pair_swe = VMODEL_PAIRS.get(swe)
        if pair_swe:
            # Find the pair stage
            pair_stages = [s for s in stages if s["swe_level"] == pair_swe]
            if pair_stages:
                pair_stage = pair_stages[0]
                completeness = TraceabilityModel.get_completeness_for_pair(
                    stage["id"], pair_stage["id"], conn
                )
                lines.append(f"### Traceability to {pair_swe} / {pair_swe} 추적성")
                lines.append("")
                lines.append(f"- Links / 링크: {completeness['link_count']}")
                lines.append(f"- Linked documents / 연결된 문서: {completeness['linked_docs']}/{completeness['total_docs']}")
                lines.append(f"- Completeness / 완성도: {completeness['completeness_pct']:.0f}%")
                lines.append("")

        lines.append("---")
        lines.append("")

    if should_close:
        conn.close()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
