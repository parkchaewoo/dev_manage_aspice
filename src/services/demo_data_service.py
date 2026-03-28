"""데모 데이터 서비스 - 기본 OEM 3개 + 예시 프로젝트 3개 생성"""
import os
from datetime import date
from src.models.oem import OemModel
from src.models.project import ProjectModel
from src.models.stage import StageModel
from src.models.document import DocumentModel
from src.models.checklist import ChecklistModel
from src.models.traceability import TraceabilityModel
from src.models.schedule import ScheduleModel
from src.models.phase import PhaseModel
from src.models.phase_log import PhaseLogModel
from src.utils.constants import SWE_STAGES
from src.utils.yaml_helpers import load_yaml, dump_yaml_string


def _load_oem_yaml(filename):
    """config/default_oem_configs/에서 YAML 로드"""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, "config", "default_oem_configs", filename)
    try:
        data = load_yaml(path)
        return dump_yaml_string(data)
    except Exception:
        return ""


def _fill_demo_content(content, project_name, oem_name, swe_level):
    """Replace ___ placeholders with realistic automotive sample data for demo projects."""
    # Determine project type from project_name / oem_name
    pname_lower = (project_name or "").lower()
    oem_lower = (oem_name or "").lower()

    if "steering" in pname_lower or "조향" in pname_lower or "hkmc" in oem_lower:
        return _fill_steering_demo(content, swe_level)
    elif "brake" in pname_lower or "브레이크" in pname_lower or "volkswagen" in oem_lower or "vw" in oem_lower:
        return _fill_brake_demo(content, swe_level)
    elif "navi" in pname_lower or "네비" in pname_lower or "gm" in oem_lower:
        return _fill_navigation_demo(content, swe_level)
    return content


def _fill_steering_demo(content, swe_level):
    """Fill ___ with HKMC EPS steering system sample data."""
    replacements = {
        "SWE.1": [
            ("| SWE1-REQ-001 | ___ |", "| SWE1-REQ-001 | SW shall read steering angle sensor input within ±720° / 조향각 센서 입력을 ±720° 범위 내에서 읽어야 한다 |"),
            ("| SWE1-REQ-002 | ___ |", "| SWE1-REQ-002 | SW shall calculate assist torque in range 0~12 Nm / 보조 토크를 0~12 Nm 범위에서 계산해야 한다 |"),
            ("| SWE1-REQ-003 | ___ |", "| SWE1-REQ-003 | SW shall detect sensor failure within 10ms / 센서 고장을 10ms 이내에 감지해야 한다 |"),
            ("| SWE1-NFR-001 | ___ | ___ |", "| SWE1-NFR-001 | Main control loop cycle time / 메인 제어 루프 주기 | ≤ 5 ms |"),
            ("| SWE1-NFR-002 | ___ | ___ |", "| SWE1-NFR-002 | Boot time / 부팅 시간 | ≤ 200 ms |"),
            ("| SWE1-NFR-003 | ___ | ___ |", "| SWE1-NFR-003 | RAM usage / RAM 사용량 | ≤ 70% |"),
        ],
        "SWE.2": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가",
             "| SensorInput | Reads and filters steering angle sensor / 조향각 센서 읽기 및 필터링 | ADC raw data | Filtered angle |\n| ControlLogic | PID torque calculation / PID 토크 계산 | Angle, Speed | Torque command |\n| SafetyMonitor | Fault detection and safe state management / 고장 감지 및 안전 상태 관리 | All status | Safety state |\n| (추가"),
            ("| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| (추가",
             "| SteeringAngle | SensorInput | ControlLogic | FLOAT32 | 5ms |\n| TargetTorque | ControlLogic | ActuatorOutput | FLOAT32 | 5ms |\n| SafetyState | SafetyMonitor | ControlLogic | ENUM | 5ms |\n| (추가"),
        ],
        "SWE.3": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가 / Add more) | | | |\n\n---\n\n## 2.",
             "| CalcAssistTorque | angle, speed | torque (Nm) | PID control calculation / PID 제어 계산 |\n| ReadSteeringAngle | - | angle (deg) | Read and filter sensor / 센서 읽기 및 필터링 |\n| UpdateSafetyState | fault_mask | safety_state | Check faults and transition state / 고장 확인 및 상태 전이 |\n| (추가 / Add more) | | | |\n\n---\n\n## 2."),
        ],
        "SWE.4": [
            ("| UT-001 | ___ | ___ | ___ | ___ |", "| UT-001 | CalcAssistTorque | Normal: angle=10°, speed=50km/h | torque=3.5 Nm | torque=3.5 Nm |"),
            ("| UT-002 | ___ | ___ | ___ | ___ |", "| UT-002 | ReadSteeringAngle | Max positive input | angle=720.0° | angle=720.0° |"),
            ("| UT-003 | ___ | ___ | ___ | ___ |", "| UT-003 | UpdateSafetyState | Critical fault input | state=SAFE_STATE | state=SAFE_STATE |"),
        ],
        "SWE.5": [
            ("| IT-001 | ___ | ___ | ___ | ___ |", "| IT-001 | SensorInput→ControlLogic | Steering angle data flow | angle=45.0° received | angle=45.0° received |"),
            ("| IT-002 | ___ | ___ | ___ | ___ |", "| IT-002 | ControlLogic→ActuatorOutput | Torque command chain | torque=5.0 Nm output | torque=5.0 Nm output |"),
            ("| IT-003 | ___ | ___ | ___ | ___ |", "| IT-003 | CAN→ControlLogic | Vehicle speed signal (CAN 0x123) | Speed parsed correctly | Speed parsed correctly |"),
            ("| ___ | ___ ms | ___ ms |", "| Main control loop | 5.0 ms | 4.2 ms |"),
        ],
        "SWE.6": [
            ("| SWE1-REQ-001 | QT-001 | ___ |", "| SWE1-REQ-001 | QT-001 | Steering angle input range test / 조향각 입력 범위 시험 |"),
            ("| SWE1-REQ-002 | QT-002 | ___ |", "| SWE1-REQ-002 | QT-002 | Assist torque output accuracy / 보조 토크 출력 정확도 |"),
            ("| SWE1-REQ-003 | QT-003 | ___ |", "| SWE1-REQ-003 | QT-003 | Safety response time test / 안전 응답 시간 시험 |"),
        ],
    }
    for old, new in replacements.get(swe_level, []):
        content = content.replace(old, new)
    # Fill remaining ___ with author name
    content = content.replace("| Author | ___ |", "| Author | Kim Minjun |")
    return content


def _fill_brake_demo(content, swe_level):
    """Fill ___ with VW ABS/ESC brake system sample data."""
    replacements = {
        "SWE.1": [
            ("| SWE1-REQ-001 | ___ |", "| SWE1-REQ-001 | SW shall read wheel speed sensors (4 channels) / 휠 속도 센서 4채널을 읽어야 한다 |"),
            ("| SWE1-REQ-002 | ___ |", "| SWE1-REQ-002 | SW shall calculate brake pressure for ABS control / ABS 제어를 위한 브레이크 압력을 계산해야 한다 |"),
            ("| SWE1-REQ-003 | ___ |", "| SWE1-REQ-003 | SW shall activate ESC within 20ms of instability / 불안정 감지 20ms 이내에 ESC를 작동해야 한다 |"),
            ("| SWE1-NFR-001 | ___ | ___ |", "| SWE1-NFR-001 | ABS control loop cycle / ABS 제어 루프 주기 | ≤ 2 ms |"),
            ("| SWE1-NFR-002 | ___ | ___ |", "| SWE1-NFR-002 | ESC response time / ESC 응답 시간 | ≤ 20 ms |"),
            ("| SWE1-NFR-003 | ___ | ___ |", "| SWE1-NFR-003 | CPU load under braking / 제동 시 CPU 부하 | ≤ 75% |"),
        ],
        "SWE.2": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가",
             "| WheelSpeedInput | Reads 4 wheel speed sensors / 4채널 휠 속도 센서 읽기 | Sensor raw data | Filtered speed |\n| ABSController | Anti-lock braking algorithm / ABS 알고리즘 | Wheel speeds | Brake pressure cmd |\n| ESCController | Electronic stability control / 전자 안정성 제어 | Yaw rate, lateral accel | Brake distribution |\n| (추가"),
            ("| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| (추가",
             "| WheelSpeed_FL | WheelSpeedInput | ABSController | FLOAT32 | 2ms |\n| BrakePressure | ABSController | HydraulicValve | FLOAT32 | 2ms |\n| YawRate | IMU | ESCController | FLOAT32 | 5ms |\n| (추가"),
        ],
        "SWE.3": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가 / Add more) | | | |\n\n---\n\n## 2.",
             "| CalcBrakePressure | wheel_speeds, pedal_force | pressure (bar) | ABS pressure calculation / ABS 압력 계산 |\n| DetectWheelLock | wheel_speed, vehicle_speed | is_locked (bool) | Wheel lock detection / 휠 잠김 감지 |\n| CalcYawCorrection | yaw_rate, target_yaw | correction (Nm) | ESC yaw correction / ESC 요 보정 |\n| (추가 / Add more) | | | |\n\n---\n\n## 2."),
        ],
        "SWE.4": [
            ("| UT-001 | ___ | ___ | ___ | ___ |", "| UT-001 | CalcBrakePressure | Normal braking: pedal=50% | pressure=40 bar | pressure=40 bar |"),
            ("| UT-002 | ___ | ___ | ___ | ___ |", "| UT-002 | DetectWheelLock | Wheel slip > 15% | is_locked=TRUE | is_locked=TRUE |"),
            ("| UT-003 | ___ | ___ | ___ | ___ |", "| UT-003 | CalcYawCorrection | Oversteer condition | correction=25 Nm | correction=25 Nm |"),
        ],
        "SWE.5": [
            ("| IT-001 | ___ | ___ | ___ | ___ |", "| IT-001 | WheelSpeed→ABSController | Wheel speed data flow | 4ch speeds received | 4ch speeds received |"),
            ("| IT-002 | ___ | ___ | ___ | ___ |", "| IT-002 | ABSController→HydraulicValve | Brake pressure command | pressure=40 bar output | pressure=40 bar output |"),
            ("| IT-003 | ___ | ___ | ___ | ___ |", "| IT-003 | IMU→ESCController | Yaw rate signal | Yaw rate parsed correctly | Yaw rate parsed correctly |"),
            ("| ___ | ___ ms | ___ ms |", "| ABS control loop | 2.0 ms | 1.6 ms |"),
        ],
        "SWE.6": [
            ("| SWE1-REQ-001 | QT-001 | ___ |", "| SWE1-REQ-001 | QT-001 | Wheel speed sensor reading test / 휠 속도 센서 읽기 시험 |"),
            ("| SWE1-REQ-002 | QT-002 | ___ |", "| SWE1-REQ-002 | QT-002 | ABS brake pressure accuracy / ABS 브레이크 압력 정확도 |"),
            ("| SWE1-REQ-003 | QT-003 | ___ |", "| SWE1-REQ-003 | QT-003 | ESC activation response time / ESC 작동 응답 시간 시험 |"),
        ],
    }
    for old, new in replacements.get(swe_level, []):
        content = content.replace(old, new)
    content = content.replace("| Author | ___ |", "| Author | Mueller Hans |")
    return content


def _fill_navigation_demo(content, swe_level):
    """Fill ___ with GM navigation system sample data."""
    replacements = {
        "SWE.1": [
            ("| SWE1-REQ-001 | ___ |", "| SWE1-REQ-001 | SW shall display map within 2 seconds of route request / 경로 요청 2초 이내에 지도를 표시해야 한다 |"),
            ("| SWE1-REQ-002 | ___ |", "| SWE1-REQ-002 | SW shall calculate route within 5 seconds / 5초 이내에 경로를 계산해야 한다 |"),
            ("| SWE1-REQ-003 | ___ |", "| SWE1-REQ-003 | SW shall update GPS position every 1 second / 1초마다 GPS 위치를 갱신해야 한다 |"),
            ("| SWE1-NFR-001 | ___ | ___ |", "| SWE1-NFR-001 | Map rendering frame rate / 지도 렌더링 프레임률 | ≥ 30 fps |"),
            ("| SWE1-NFR-002 | ___ | ___ |", "| SWE1-NFR-002 | Route calculation time / 경로 계산 시간 | ≤ 5 sec |"),
            ("| SWE1-NFR-003 | ___ | ___ |", "| SWE1-NFR-003 | Memory usage / 메모리 사용량 | ≤ 512 MB |"),
        ],
        "SWE.2": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가",
             "| MapRenderer | Renders map tiles on display / 지도 타일 렌더링 | Map data, GPS pos | Display output |\n| RouteEngine | Calculates optimal route / 최적 경로 계산 | Start, Destination | Route path |\n| GPSManager | Manages GPS position updates / GPS 위치 갱신 관리 | GPS signal | Lat/Lon/Heading |\n| (추가"),
            ("| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ | ___ |\n| (추가",
             "| GPSPosition | GPSManager | MapRenderer | STRUCT | 1s |\n| RouteData | RouteEngine | MapRenderer | STRUCT | On request |\n| UserInput | HMI | RouteEngine | EVENT | On input |\n| (추가"),
        ],
        "SWE.3": [
            ("| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| ___ | ___ | ___ | ___ |\n| (추가 / Add more) | | | |\n\n---\n\n## 2.",
             "| CalcRoute | start, destination | route_path | A* pathfinding algorithm / A* 경로 탐색 |\n| RenderMapTile | tile_id, zoom_level | pixel_buffer | Map tile rendering / 지도 타일 렌더링 |\n| UpdateGPSPosition | raw_gps_data | lat, lon, heading | GPS signal processing / GPS 신호 처리 |\n| (추가 / Add more) | | | |\n\n---\n\n## 2."),
        ],
        "SWE.4": [
            ("| UT-001 | ___ | ___ | ___ | ___ |", "| UT-001 | CalcRoute | Short route: 5km distance | Route found in < 1s | Route found in 0.8s |"),
            ("| UT-002 | ___ | ___ | ___ | ___ |", "| UT-002 | RenderMapTile | Zoom level 15, urban area | Tile rendered < 33ms | Tile rendered in 28ms |"),
            ("| UT-003 | ___ | ___ | ___ | ___ |", "| UT-003 | UpdateGPSPosition | Valid GPS signal | Position accuracy < 3m | Position accuracy 2.1m |"),
        ],
        "SWE.5": [
            ("| IT-001 | ___ | ___ | ___ | ___ |", "| IT-001 | GPSManager→MapRenderer | GPS position to map display | Map centers on position | Map centers on position |"),
            ("| IT-002 | ___ | ___ | ___ | ___ |", "| IT-002 | RouteEngine→MapRenderer | Route overlay on map | Route drawn correctly | Route drawn correctly |"),
            ("| IT-003 | ___ | ___ | ___ | ___ |", "| IT-003 | HMI→RouteEngine | User destination input | Route calculated < 5s | Route calculated in 3.2s |"),
            ("| ___ | ___ ms | ___ ms |", "| Map tile rendering | 33.0 ms | 28.0 ms |"),
        ],
        "SWE.6": [
            ("| SWE1-REQ-001 | QT-001 | ___ |", "| SWE1-REQ-001 | QT-001 | Map display response time test / 지도 표시 응답 시간 시험 |"),
            ("| SWE1-REQ-002 | QT-002 | ___ |", "| SWE1-REQ-002 | QT-002 | Route calculation time test / 경로 계산 시간 시험 |"),
            ("| SWE1-REQ-003 | QT-003 | ___ |", "| SWE1-REQ-003 | QT-003 | GPS update frequency test / GPS 갱신 주기 시험 |"),
        ],
    }
    for old, new in replacements.get(swe_level, []):
        content = content.replace(old, new)
    content = content.replace("| Author | ___ |", "| Author | Smith John |")
    return content


def _load_template_for_doc(template_id, project_name="", oem_name="", swe_level=""):
    """Load template content for a document's template_type, filling placeholders."""
    from src.services.export_service import _TEMPLATE_MAP, _TEMPLATES_DIR
    filename = _TEMPLATE_MAP.get(template_id) if template_id else None
    # Fallback: if template_id is empty or file not found, use SWE level
    if not filename and swe_level:
        filename = _TEMPLATE_MAP.get(swe_level)
    if not filename:
        return ""
    path = os.path.join(_TEMPLATES_DIR, filename)
    if not os.path.isfile(path):
        # Second fallback: try SWE level if template_id file was missing
        if swe_level and template_id:
            fallback_filename = _TEMPLATE_MAP.get(swe_level)
            if fallback_filename:
                path = os.path.join(_TEMPLATES_DIR, fallback_filename)
                if not os.path.isfile(path):
                    return ""
            else:
                return ""
        else:
            return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("{project_name}", project_name)
        content = content.replace("{oem_name}", oem_name)
        content = content.replace("{date}", str(date.today()))
        # Fill other common placeholders with defaults
        content = content.replace("{document_id}", "")
        content = content.replace("{document_name}", "")
        content = content.replace("{status}", "Draft")
        content = content.replace("{swe_level}", "")
        # Fill ___ placeholders with demo sample data for demo projects
        if project_name and oem_name:
            content = _fill_demo_content(content, project_name, oem_name, swe_level)
        return content
    except Exception:
        return ""


def _create_stages_from_config(project_id, config_yaml_str, conn, phase_id=None):
    """OEM 설정에 기반하여 단계/문서/체크리스트 생성"""
    from src.utils.yaml_helpers import load_yaml_string
    config = load_yaml_string(config_yaml_str) if config_yaml_str else {}
    stages_config = config.get("stages", {})

    stage_ids = {}
    doc_ids = {}

    # Get project and OEM names for template placeholder filling
    project = ProjectModel.get_by_id(project_id, conn)
    project_name = project["name"] if project else ""
    oem_name = ""
    if project:
        oem = OemModel.get_by_id(project["oem_id"], conn)
        oem_name = oem["name"] if oem else ""

    for swe_level in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
        stage_conf = stages_config.get(swe_level, {})
        if stage_conf.get("enabled", True) is False:
            continue

        stage_id = StageModel.create(project_id, swe_level, phase_id=phase_id, conn=conn)
        stage_ids[swe_level] = stage_id

        # 문서 생성
        docs = stage_conf.get("required_documents", [])
        if not docs:
            # 기본 문서
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

        swe_doc_ids = []
        for doc_info in docs:
            doc_name = doc_info.get("name", "Unnamed Document")
            template_id = doc_info.get("template_id", "")
            did = DocumentModel.create(stage_id, doc_name, template_type=template_id, conn=conn)
            swe_doc_ids.append(did)

            # Load and set template content for the document
            if template_id or swe_level:
                content = _load_template_for_doc(template_id, project_name, oem_name, swe_level=swe_level)
                if content:
                    DocumentModel.update(did, content=content, conn=conn)
        doc_ids[swe_level] = swe_doc_ids

        # 체크리스트 생성
        checklist = stage_conf.get("checklist", [])
        if not checklist:
            default_checklists = {
                "SWE.1": ["All requirements have unique IDs / 모든 요구사항에 고유 ID 부여",
                          "Requirements are testable / 요구사항 시험 가능성 확인",
                          "Traceability to system requirements / 시스템 요구사항 추적성 확인",
                          "Review completed / 검토 완료"],
                "SWE.2": ["Architecture addresses all requirements / 아키텍처가 모든 요구사항을 반영",
                          "Interface descriptions complete / 인터페이스 기술 완료",
                          "Resource constraints considered / 리소스 제약 고려",
                          "Review completed / 검토 완료"],
                "SWE.3": ["Detailed design matches architecture / 상세 설계가 아키텍처와 일치",
                          "Coding guidelines followed / 코딩 가이드라인 준수",
                          "Static analysis passed / 정적 분석 통과",
                          "Code review completed / 코드 리뷰 완료"],
                "SWE.4": ["Unit test plan reviewed / 단위 시험 계획 검토",
                          "Coverage targets met / 커버리지 목표 달성",
                          "All test cases passed / 모든 테스트 통과",
                          "Test report reviewed / 시험 보고서 검토"],
                "SWE.5": ["Integration strategy defined / 통합 전략 정의",
                          "Interface tests passed / 인터페이스 시험 통과",
                          "Timing requirements met / 타이밍 요구사항 충족",
                          "Integration report reviewed / 통합 보고서 검토"],
                "SWE.6": ["All requirements covered / 모든 요구사항 커버",
                          "Test environment validated / 시험 환경 검증",
                          "All test cases executed / 모든 시험 실행",
                          "Qualification report approved / 적격성 보고서 승인"],
            }
            checklist = default_checklists.get(swe_level, [])

        for item in checklist:
            ChecklistModel.create(stage_id, item, conn=conn)

    return stage_ids, doc_ids


def _complete_all_stages(stage_ids, doc_ids, user, conn):
    """Helper: mark all stages Completed, all docs Approved, all checklists checked."""
    for swe in ["SWE.1", "SWE.2", "SWE.3", "SWE.4", "SWE.5", "SWE.6"]:
        if swe in stage_ids:
            StageModel.update(stage_ids[swe], status="Completed", conn=conn)
            for did in doc_ids.get(swe, []):
                DocumentModel.update(did, status="Approved", conn=conn)
            items = ChecklistModel.get_by_stage(stage_ids[swe], conn)
            for item in items:
                ChecklistModel.toggle(item["id"], user, conn)


def _create_full_traceability(doc_ids, conn):
    """Helper: create V-model + sequential traceability links for a phase."""
    # === 순차적 추적성 (derives: 상→하) ===
    # SWE.1 → SWE.2
    if doc_ids.get("SWE.1") and doc_ids.get("SWE.2"):
        TraceabilityModel.create(
            doc_ids["SWE.1"][0], doc_ids["SWE.2"][0],
            "derives", "요구사항에서 아키텍처 도출 / Requirements to Architecture", conn
        )
    # SWE.2 → SWE.3
    if doc_ids.get("SWE.2") and doc_ids.get("SWE.3"):
        TraceabilityModel.create(
            doc_ids["SWE.2"][0], doc_ids["SWE.3"][0],
            "derives", "아키텍처에서 상세설계 도출 / Architecture to Detailed Design", conn
        )

    # === V-Model 추적성 (verifies: 좌↔우) ===
    # SWE.1 <-> SWE.6
    if doc_ids.get("SWE.1") and doc_ids.get("SWE.6"):
        TraceabilityModel.create(
            doc_ids["SWE.1"][0], doc_ids["SWE.6"][0],
            "verifies", "요구사항 적격성 시험 추적", conn
        )
        if len(doc_ids["SWE.1"]) > 1 and len(doc_ids["SWE.6"]) > 1:
            TraceabilityModel.create(
                doc_ids["SWE.1"][1], doc_ids["SWE.6"][1],
                "verifies", "검토 보고서 추적", conn
            )
    # SWE.2 <-> SWE.5
    if doc_ids.get("SWE.2") and doc_ids.get("SWE.5"):
        TraceabilityModel.create(
            doc_ids["SWE.2"][0], doc_ids["SWE.5"][0],
            "verifies", "아키텍처 통합 시험 추적", conn
        )
    # SWE.3 <-> SWE.4
    if doc_ids.get("SWE.3") and doc_ids.get("SWE.4"):
        TraceabilityModel.create(
            doc_ids["SWE.3"][0], doc_ids["SWE.4"][0],
            "verifies", "상세 설계 단위 검증 추적", conn
        )


def create_demo_data(conn):
    """데모 데이터 생성"""
    # === OEM 생성 ===
    hkmc_yaml = _load_oem_yaml("hkmc.yaml")
    vw_yaml = _load_oem_yaml("volkswagen.yaml")
    gm_yaml = _load_oem_yaml("gm.yaml")

    hkmc_id = OemModel.create("HKMC", "현대기아자동차그룹 / Hyundai Kia Motor Company", hkmc_yaml, conn)
    vw_id = OemModel.create("Volkswagen", "Volkswagen Group", vw_yaml, conn)
    gm_id = OemModel.create("GM", "General Motors", gm_yaml, conn)

    # === 프로젝트 1: HKMC 조향 시스템 ===
    proj1_id = ProjectModel.create(
        hkmc_id, "조향 시스템 (Steering System)",
        "EPS 전동 조향 시스템 소프트웨어 개발",
        "Active", "2026-01-15", "2026-12-31", conn
    )

    # --- Mcar phase (ASPICE 100% 완료) ---
    mcar_phase_id = PhaseModel.create(proj1_id, "Mcar", "Mcar 개발 단계 - 100% 완료", 1, conn=conn)
    stage_ids_mcar, doc_ids_mcar = _create_stages_from_config(
        proj1_id, hkmc_yaml, conn, phase_id=mcar_phase_id
    )
    _complete_all_stages(stage_ids_mcar, doc_ids_mcar, "HKMC Engineer", conn)
    _create_full_traceability(doc_ids_mcar, conn)
    PhaseLogModel.create(mcar_phase_id, "created", "phase", mcar_phase_id,
                         "Mcar phase created - ASPICE 100% complete", "System", conn=conn)

    # --- P1 phase (진행중, inherited from Mcar) ---
    p1_phase_id = PhaseModel.create(proj1_id, "P1", "P1 개발 단계 - 진행중", 2,
                                     inherited_from_phase_id=mcar_phase_id, conn=conn)
    stage_ids_p1, doc_ids_p1 = _create_stages_from_config(
        proj1_id, hkmc_yaml, conn, phase_id=p1_phase_id
    )

    # P1: SWE.1-2 Completed, SWE.3 In Progress
    for swe in ["SWE.1", "SWE.2"]:
        if swe in stage_ids_p1:
            StageModel.update(stage_ids_p1[swe], status="Completed", conn=conn)
            for did in doc_ids_p1.get(swe, []):
                DocumentModel.update(did, status="Approved", conn=conn)
            items = ChecklistModel.get_by_stage(stage_ids_p1[swe], conn)
            for item in items:
                ChecklistModel.toggle(item["id"], "HKMC Engineer", conn)

    if "SWE.3" in stage_ids_p1:
        StageModel.update(stage_ids_p1["SWE.3"], status="In Progress", conn=conn)
        docs = doc_ids_p1.get("SWE.3", [])
        if docs:
            DocumentModel.update(docs[0], status="In Review", conn=conn)

    # P1 traceability
    _create_full_traceability(doc_ids_p1, conn)

    PhaseLogModel.create(p1_phase_id, "inherited", "phase", p1_phase_id,
                         "P1 phase inherited from Mcar", "System", conn=conn)

    # 마일스톤
    ScheduleModel.create(proj1_id, "SWE.1 Requirements Complete", "2026-03-01",
                         stage_ids_mcar.get("SWE.1"), "Completed", conn)
    ScheduleModel.create(proj1_id, "SWE.2 Architecture Review", "2026-05-01",
                         stage_ids_p1.get("SWE.2"), "Completed", conn)
    ScheduleModel.create(proj1_id, "SWE.6 Final Qualification", "2026-11-30",
                         stage_ids_p1.get("SWE.6"), "Pending", conn)

    # === 프로젝트 2: VW BRAKE 시스템 ===
    proj2_id = ProjectModel.create(
        vw_id, "BRAKE System (브레이크 시스템)",
        "ABS/ESC 브레이크 제어 시스템 소프트웨어",
        "Active", "2026-02-01", "2027-03-31", conn
    )

    # --- A-Muster phase (완료) ---
    a_muster_id = PhaseModel.create(proj2_id, "A-Muster", "A-Muster 개발 단계 - 완료", 1, conn=conn)
    stage_ids_am, doc_ids_am = _create_stages_from_config(
        proj2_id, vw_yaml, conn, phase_id=a_muster_id
    )
    _complete_all_stages(stage_ids_am, doc_ids_am, "VW Engineer", conn)
    _create_full_traceability(doc_ids_am, conn)
    PhaseLogModel.create(a_muster_id, "created", "phase", a_muster_id,
                         "A-Muster phase created - fully complete", "System", conn=conn)

    # --- B-Muster phase (진행중, inherited from A-Muster) ---
    b_muster_id = PhaseModel.create(proj2_id, "B-Muster", "B-Muster 개발 단계 - 진행중", 2,
                                     inherited_from_phase_id=a_muster_id, conn=conn)
    stage_ids_bm, doc_ids_bm = _create_stages_from_config(
        proj2_id, vw_yaml, conn, phase_id=b_muster_id
    )

    # B-Muster: SWE.1-2 Completed (inherited), SWE.3 In Progress
    for swe in ["SWE.1", "SWE.2"]:
        if swe in stage_ids_bm:
            StageModel.update(stage_ids_bm[swe], status="Completed", conn=conn)
            for did in doc_ids_bm.get(swe, []):
                DocumentModel.update(did, status="Approved", conn=conn)
            items = ChecklistModel.get_by_stage(stage_ids_bm[swe], conn)
            for item in items:
                ChecklistModel.toggle(item["id"], "VW Engineer", conn)

    if "SWE.3" in stage_ids_bm:
        StageModel.update(stage_ids_bm["SWE.3"], status="In Progress", conn=conn)

    _create_full_traceability(doc_ids_bm, conn)

    PhaseLogModel.create(b_muster_id, "inherited", "phase", b_muster_id,
                         "B-Muster phase inherited from A-Muster", "System", conn=conn)

    ScheduleModel.create(proj2_id, "SWE.1 Complete", "2026-04-15",
                         stage_ids_am.get("SWE.1"), "Completed", conn)
    ScheduleModel.create(proj2_id, "SWE.3 Code Freeze", "2026-08-01",
                         stage_ids_bm.get("SWE.3"), "Pending", conn)

    # === 프로젝트 3: GM Navigation ===
    proj3_id = ProjectModel.create(
        gm_id, "Navigation System (네비게이션)",
        "차량 내비게이션 소프트웨어 개발",
        "Active", "2026-03-01", "2027-06-30", conn
    )

    # --- DV phase (시작) ---
    dv_phase_id = PhaseModel.create(proj3_id, "DV", "DV 개발 단계 - 시작", 1, conn=conn)
    stage_ids_dv, doc_ids_dv = _create_stages_from_config(
        proj3_id, gm_yaml, conn, phase_id=dv_phase_id
    )

    # DV: SWE.1 In Progress only
    if "SWE.1" in stage_ids_dv:
        StageModel.update(stage_ids_dv["SWE.1"], status="In Progress", conn=conn)
        docs = doc_ids_dv.get("SWE.1", [])
        if docs:
            DocumentModel.update(docs[0], status="In Review", conn=conn)

    PhaseLogModel.create(dv_phase_id, "created", "phase", dv_phase_id,
                         "DV phase created - SWE.1 in progress", "System", conn=conn)

    ScheduleModel.create(proj3_id, "SWE.1 Requirements Review", "2026-05-15",
                         stage_ids_dv.get("SWE.1"), "Pending", conn)
    ScheduleModel.create(proj3_id, "Project Kickoff Complete", "2026-03-15",
                         None, "Completed", conn)

    conn.commit()
