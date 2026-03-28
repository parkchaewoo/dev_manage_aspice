"""Phase 관리 서비스 - 개발 단계 생성 및 상속"""
from src.models.database import get_connection
from src.models.phase import PhaseModel
from src.models.phase_log import PhaseLogModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel


def create_phase_from_template(project_id, phase_name, description="", conn=None):
    """Create a new empty phase with full SWE.1~6 stages.

    Creates the phase, 6 SWE stages, and populates default documents
    and checklists from the project's OEM configuration.
    """
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    # Determine phase_order
    existing = PhaseModel.get_by_project(project_id, conn)
    phase_order = len(existing) + 1

    # Create Phase record
    phase_id = PhaseModel.create(
        project_id, phase_name, description, phase_order, conn=conn
    )

    # Get OEM config for this project
    from src.models.project import ProjectModel
    from src.models.oem import OemModel
    from src.utils.yaml_helpers import load_yaml_string

    project = ProjectModel.get_by_id(project_id, conn)
    oem = OemModel.get_by_id(project["oem_id"], conn)
    config = load_yaml_string(oem["config_yaml"]) if oem and oem["config_yaml"] else {}
    stages_config = config.get("stages", {})

    # Create 6 stages under the phase
    for swe_level in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
        stage_conf = stages_config.get(swe_level, {})
        if stage_conf.get("enabled", True) is False:
            continue

        stage_id = StageModel.create(project_id, swe_level, phase_id=phase_id, conn=conn)

        # Create documents from config
        docs = stage_conf.get("required_documents", [])
        if not docs:
            default_docs = {
                "SWE.1": [("Software Requirements Specification (SRS)", "srs"),
                          ("Requirements Review Report", "req_review")],
                "SWE.2": [("Software Architecture Document (SAD)", "sad"),
                          ("Interface Design Document", "idd")],
                "SWE.3": [("Software Detailed Design (SDD)", "sdd"),
                          ("Source Code", "code")],
                "SWE.4": [("Unit Test Plan", "ut_plan"),
                          ("Unit Test Report", "ut_report")],
                "SWE.5": [("Integration Test Plan", "it_plan"),
                          ("Integration Test Report", "it_report")],
                "SWE.6": [("Qualification Test Plan", "qt_plan"),
                          ("Qualification Test Report", "qt_report")],
            }
            docs = [{"name": n, "template_id": t} for n, t in default_docs.get(swe_level, [])]

        for doc_info in docs:
            doc_name = doc_info.get("name", "Unnamed Document")
            template_id = doc_info.get("template_id", "")
            DocumentModel.create(stage_id, doc_name, template_type=template_id, conn=conn)

        # Create checklists from config
        checklist = stage_conf.get("checklist", [])
        if not checklist:
            default_checklists = {
                "SWE.1": ["All requirements have unique IDs",
                          "Requirements are testable",
                          "Traceability to system requirements",
                          "Review completed"],
                "SWE.2": ["Architecture addresses all requirements",
                          "Interface descriptions complete",
                          "Resource constraints considered",
                          "Review completed"],
                "SWE.3": ["Detailed design matches architecture",
                          "Coding guidelines followed",
                          "Static analysis passed",
                          "Code review completed"],
                "SWE.4": ["Unit test plan reviewed",
                          "Coverage targets met",
                          "All test cases passed",
                          "Test report reviewed"],
                "SWE.5": ["Integration strategy defined",
                          "Interface tests passed",
                          "Timing requirements met",
                          "Integration report reviewed"],
                "SWE.6": ["All requirements covered",
                          "Test environment validated",
                          "All test cases executed",
                          "Qualification report approved"],
            }
            checklist = default_checklists.get(swe_level, [])

        for item in checklist:
            ChecklistModel.create(stage_id, item, conn=conn)

    # Log creation
    PhaseLogModel.create(
        phase_id, "created", "phase", phase_id,
        f"Phase '{phase_name}' created from template", "System", conn=conn
    )

    if should_close:
        conn.close()

    return phase_id


def create_phase_inherited(project_id, phase_name, source_phase_id, description="", conn=None):
    """Create a new phase inheriting from a previous phase.

    Copies Approved documents (keeping status), skips Draft/In Review docs,
    copies checklist items with their checked state, and copies traceability links.
    """
    should_close = conn is None
    if conn is None:
        conn = get_connection()

    # Determine phase_order
    existing = PhaseModel.get_by_project(project_id, conn)
    phase_order = len(existing) + 1

    # Create Phase record with inherited_from_phase_id
    phase_id = PhaseModel.create(
        project_id, phase_name, description, phase_order,
        inherited_from_phase_id=source_phase_id, conn=conn
    )

    # Get source phase stages
    source_stages = StageModel.get_by_phase(source_phase_id, conn)

    # Map old doc IDs to new doc IDs for traceability
    doc_id_map = {}

    for source_stage in source_stages:
        # Create new stage under new phase
        new_stage_id = StageModel.create(
            project_id, source_stage["swe_level"],
            status=source_stage["status"],
            phase_id=phase_id, conn=conn
        )

        # Copy documents - only Approved ones keep status, skip Draft/In Review
        source_docs = DocumentModel.get_by_stage(source_stage["id"], conn)
        for doc in source_docs:
            if doc["status"] == "Approved":
                new_doc_id = DocumentModel.create(
                    new_stage_id, doc["name"],
                    template_type=doc["template_type"],
                    file_path=doc["file_path"],
                    status="Approved",
                    reviewer=doc["reviewer"],
                    notes=f"[Inherited] {doc['notes'] or ''}".strip(),
                    conn=conn
                )
                doc_id_map[doc["id"]] = new_doc_id

                PhaseLogModel.create(
                    phase_id, "inherited", "document", new_doc_id,
                    f"Document '{doc['name']}' inherited from phase",
                    "System", conn=conn
                )
            # Skip Draft/In Review documents

        # Copy checklist items with their checked state
        source_items = ChecklistModel.get_by_stage(source_stage["id"], conn)
        for item in source_items:
            new_item_id = ChecklistModel.create(
                new_stage_id, item["description"], conn=conn
            )
            if item["is_checked"]:
                ChecklistModel.toggle(
                    new_item_id, item["checked_by"] or "Inherited", conn=conn
                )

    # Copy traceability links (mapping old doc IDs to new doc IDs)
    for old_src_id, new_src_id in doc_id_map.items():
        source_links = conn.execute(
            """SELECT * FROM traceability_links
               WHERE source_document_id = ? OR target_document_id = ?""",
            (old_src_id, old_src_id)
        ).fetchall()

        for link in source_links:
            old_target = link["target_document_id"] if link["source_document_id"] == old_src_id else link["source_document_id"]
            if old_target in doc_id_map:
                new_target_id = doc_id_map[old_target]
                if link["source_document_id"] == old_src_id:
                    new_source_doc = new_src_id
                    new_target_doc = new_target_id
                else:
                    new_source_doc = new_target_id
                    new_target_doc = new_src_id

                # Check if this link already exists
                exists = conn.execute(
                    """SELECT COUNT(*) FROM traceability_links
                       WHERE source_document_id = ? AND target_document_id = ?""",
                    (new_source_doc, new_target_doc)
                ).fetchone()[0]

                if not exists:
                    TraceabilityModel.create(
                        new_source_doc, new_target_doc,
                        link["link_type"],
                        f"[Inherited] {link['description'] or ''}".strip(),
                        conn=conn
                    )

    # Log inheritance
    PhaseLogModel.create(
        phase_id, "inherited", "phase", phase_id,
        f"Phase '{phase_name}' inherited from phase #{source_phase_id}",
        "System", conn=conn
    )

    if should_close:
        conn.close()

    return phase_id
