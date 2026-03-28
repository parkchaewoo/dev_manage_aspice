"""데모 데이터 서비스 - 기본 OEM 3개 + 예시 프로젝트 3개 생성"""
import json
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


def _create_demo_items(project_name, oem_name, swe_level):
    """Create demo JSON items for a document based on project type and SWE level.

    Returns a JSON string with 3-5 sample items appropriate for the SWE stage.
    """
    pname_lower = (project_name or "").lower()
    oem_lower = (oem_name or "").lower()

    if "steering" in pname_lower or "조향" in pname_lower or "hkmc" in oem_lower:
        items = _steering_items(swe_level)
    elif "brake" in pname_lower or "브레이크" in pname_lower or "volkswagen" in oem_lower or "vw" in oem_lower:
        items = _brake_items(swe_level)
    elif "navi" in pname_lower or "네비" in pname_lower or "gm" in oem_lower:
        items = _navigation_items(swe_level)
    else:
        items = None

    if items:
        return json.dumps(items, ensure_ascii=False)
    return ""


def _steering_items(swe_level):
    """Return demo items for HKMC Steering System."""
    data = {
        "SWE.1": [
            {"id": "SWE1-REQ-001", "requirement": "SW shall read steering angle sensor input within ±720°", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-002", "requirement": "SW shall calculate assist torque in range 0-12Nm", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-003", "requirement": "SW shall detect sensor failure and enter safety mode within 10ms", "priority": "High", "verification": "Test", "notes": "Safety critical"},
            {"id": "SWE1-REQ-004", "requirement": "SW shall communicate via CAN bus with 20ms cycle time", "priority": "Medium", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-005", "requirement": "SW shall store DTC in non-volatile memory on fault detection", "priority": "Medium", "verification": "Inspection", "notes": ""},
        ],
        "SWE.2": [
            {"id": "SWE2-CMP-001", "component": "SensorInput", "responsibility": "Read and filter steering angle sensor data", "input": "ADC raw data", "output": "Filtered angle (deg)", "notes": ""},
            {"id": "SWE2-CMP-002", "component": "ControlLogic", "responsibility": "PID torque calculation based on angle and speed", "input": "Angle, Vehicle speed", "output": "Torque command (Nm)", "notes": ""},
            {"id": "SWE2-CMP-003", "component": "ActuatorOutput", "responsibility": "Drive EPS motor with torque command", "input": "Torque command", "output": "PWM signal", "notes": ""},
            {"id": "SWE2-CMP-004", "component": "SafetyMonitor", "responsibility": "Fault detection and safe state management", "input": "All sensor status", "output": "Safety state", "notes": "ASIL-D"},
            {"id": "SWE2-CMP-005", "component": "DiagManager", "responsibility": "DTC storage and diagnostic communication", "input": "Fault flags", "output": "UDS responses", "notes": ""},
        ],
        "SWE.3": [
            {"id": "SWE3-FUN-001", "function": "CalcAssistTorque", "input": "angle (deg), speed (km/h)", "output": "torque (Nm)", "description": "PID control calculation for assist torque", "notes": ""},
            {"id": "SWE3-FUN-002", "function": "ReadSteeringAngle", "input": "ADC raw value", "output": "angle (deg)", "description": "Read sensor, apply filter and range check", "notes": ""},
            {"id": "SWE3-FUN-003", "function": "CheckSensorValidity", "input": "sensor value, timestamp", "output": "is_valid (bool)", "description": "Validate sensor data against range and timing", "notes": ""},
            {"id": "SWE3-FUN-004", "function": "UpdateSafetyState", "input": "fault_mask", "output": "safety_state (enum)", "description": "Check faults and transition safety state machine", "notes": ""},
        ],
        "SWE.4": [
            {"id": "SWE4-UT-001", "function": "CalcAssistTorque", "test_desc": "Normal: angle=10deg, speed=50km/h", "expected": "torque=3.5Nm", "actual": "torque=3.5Nm", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-002", "function": "CalcAssistTorque", "test_desc": "Saturation: angle=720deg, speed=0km/h", "expected": "torque=12.0Nm (max)", "actual": "torque=12.0Nm", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-003", "function": "ReadSteeringAngle", "test_desc": "Sensor range max positive input", "expected": "angle=720.0deg", "actual": "angle=720.0deg", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-004", "function": "UpdateSafetyState", "test_desc": "Critical fault input detected", "expected": "state=SAFE_STATE", "actual": "state=SAFE_STATE", "result": "Pass", "notes": ""},
        ],
        "SWE.5": [
            {"id": "SWE5-IT-001", "interface": "SensorInput to ControlLogic", "test_desc": "Steering angle data flow verification", "expected": "angle=45.0deg received by ControlLogic", "actual": "angle=45.0deg received", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-002", "interface": "ControlLogic to ActuatorOutput", "test_desc": "CAN integration for vehicle speed signal", "expected": "Speed parsed correctly from CAN 0x123", "actual": "Speed parsed correctly", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-003", "interface": "SafetyMonitor to ControlLogic", "test_desc": "Safety fault propagation to control", "expected": "Control enters safe state within 10ms", "actual": "Safe state entered in 8ms", "result": "Pass", "notes": ""},
        ],
        "SWE.6": [
            {"id": "SWE6-QT-001", "req_id": "SWE1-REQ-001", "test_desc": "Steering angle input range test ±720deg", "expected": "Angle read within ±720deg range", "actual": "Angle read correctly at boundaries", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-002", "req_id": "SWE1-REQ-002", "test_desc": "Assist torque output accuracy 0-12Nm", "expected": "Torque within ±0.1Nm of target", "actual": "Max deviation 0.05Nm", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-003", "req_id": "SWE1-REQ-003", "test_desc": "Safety response time under fault condition", "expected": "Safe state entered within 10ms", "actual": "Safe state entered in 8ms", "result": "Pass", "notes": ""},
        ],
    }
    return data.get(swe_level)


def _brake_items(swe_level):
    """Return demo items for VW Brake System."""
    data = {
        "SWE.1": [
            {"id": "SWE1-REQ-001", "requirement": "SW shall read wheel speed sensors (4 channels) at 2ms cycle", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-002", "requirement": "SW shall calculate brake pressure for ABS control", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-003", "requirement": "SW shall activate ABS when wheel slip exceeds 15%", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-004", "requirement": "SW shall provide ESC control within 20ms of instability detection", "priority": "High", "verification": "Test", "notes": "Safety critical"},
            {"id": "SWE1-REQ-005", "requirement": "SW shall activate brake light output on brake pedal press", "priority": "Medium", "verification": "Test", "notes": ""},
        ],
        "SWE.2": [
            {"id": "SWE2-CMP-001", "component": "WheelSpeedInput", "responsibility": "Read 4 wheel speed sensors and filter data", "input": "Sensor raw data", "output": "Filtered wheel speeds", "notes": ""},
            {"id": "SWE2-CMP-002", "component": "ABSController", "responsibility": "Anti-lock braking pressure modulation", "input": "Wheel speeds, brake pedal", "output": "Brake pressure command", "notes": ""},
            {"id": "SWE2-CMP-003", "component": "ESCController", "responsibility": "Electronic stability control algorithm", "input": "Yaw rate, lateral accel", "output": "Brake distribution", "notes": "ASIL-D"},
            {"id": "SWE2-CMP-004", "component": "HydraulicValve", "responsibility": "Drive hydraulic valve actuators", "input": "Pressure command", "output": "Valve PWM signal", "notes": ""},
            {"id": "SWE2-CMP-005", "component": "DiagManager", "responsibility": "Fault storage and diagnostic services", "input": "Fault flags", "output": "UDS responses, DTC", "notes": ""},
        ],
        "SWE.3": [
            {"id": "SWE3-FUN-001", "function": "CalcBrakePressure", "input": "wheel_speeds, pedal_force", "output": "pressure (bar)", "description": "ABS pressure calculation algorithm", "notes": ""},
            {"id": "SWE3-FUN-002", "function": "DetectWheelLock", "input": "wheel_speed, vehicle_speed", "output": "is_locked (bool)", "description": "Wheel lock detection based on slip ratio", "notes": ""},
            {"id": "SWE3-FUN-003", "function": "CalcYawCorrection", "input": "yaw_rate, target_yaw", "output": "correction (Nm)", "description": "ESC yaw correction torque calculation", "notes": ""},
            {"id": "SWE3-FUN-004", "function": "FilterWheelSpeed", "input": "raw_speed_counts", "output": "filtered_speed (km/h)", "description": "Low-pass filter for wheel speed signal", "notes": ""},
        ],
        "SWE.4": [
            {"id": "SWE4-UT-001", "function": "CalcBrakePressure", "test_desc": "Normal braking: pedal=50%", "expected": "pressure=40 bar", "actual": "pressure=40 bar", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-002", "function": "DetectWheelLock", "test_desc": "Wheel slip > 15% threshold", "expected": "is_locked=TRUE", "actual": "is_locked=TRUE", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-003", "function": "CalcYawCorrection", "test_desc": "Oversteer condition detected", "expected": "correction=25Nm", "actual": "correction=25Nm", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-004", "function": "FilterWheelSpeed", "test_desc": "Noisy input at 100km/h", "expected": "filtered_speed=100.0km/h ±0.5", "actual": "filtered_speed=100.1km/h", "result": "Pass", "notes": ""},
        ],
        "SWE.5": [
            {"id": "SWE5-IT-001", "interface": "WheelSpeedInput to ABSController", "test_desc": "Wheel speed data flow for 4 channels", "expected": "4ch speeds received correctly", "actual": "4ch speeds received correctly", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-002", "interface": "ABSController to HydraulicValve", "test_desc": "Brake pressure command output chain", "expected": "pressure=40 bar output to valve", "actual": "pressure=40 bar output", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-003", "interface": "IMU to ESCController", "test_desc": "Yaw rate signal integration", "expected": "Yaw rate parsed correctly", "actual": "Yaw rate parsed correctly", "result": "Pass", "notes": ""},
        ],
        "SWE.6": [
            {"id": "SWE6-QT-001", "req_id": "SWE1-REQ-001", "test_desc": "Wheel speed sensor reading accuracy test", "expected": "4ch read at 2ms cycle", "actual": "All channels read within 2ms", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-002", "req_id": "SWE1-REQ-002", "test_desc": "ABS brake pressure calculation accuracy", "expected": "Pressure within ±1 bar", "actual": "Max deviation 0.5 bar", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-003", "req_id": "SWE1-REQ-004", "test_desc": "ESC activation response time test", "expected": "ESC active within 20ms", "actual": "ESC activated in 15ms", "result": "Pass", "notes": ""},
        ],
    }
    return data.get(swe_level)


def _navigation_items(swe_level):
    """Return demo items for GM Navigation System."""
    data = {
        "SWE.1": [
            {"id": "SWE1-REQ-001", "requirement": "SW shall acquire GPS position with accuracy < 3m", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-002", "requirement": "SW shall calculate route within 5 seconds for distances up to 500km", "priority": "High", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-003", "requirement": "SW shall render map display at minimum 30fps", "priority": "Medium", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-004", "requirement": "SW shall provide voice guidance at each maneuver point", "priority": "Medium", "verification": "Test", "notes": ""},
            {"id": "SWE1-REQ-005", "requirement": "SW shall receive and process real-time traffic data via TMC", "priority": "Low", "verification": "Test", "notes": ""},
        ],
        "SWE.2": [
            {"id": "SWE2-CMP-001", "component": "GPSManager", "responsibility": "GPS position acquisition and filtering", "input": "GPS signal", "output": "Lat/Lon/Heading", "notes": ""},
            {"id": "SWE2-CMP-002", "component": "RouteEngine", "responsibility": "Route calculation using A* algorithm", "input": "Start, Destination", "output": "Route path", "notes": ""},
            {"id": "SWE2-CMP-003", "component": "MapRenderer", "responsibility": "Map tile rendering and display", "input": "Map data, GPS pos", "output": "Display output", "notes": ""},
            {"id": "SWE2-CMP-004", "component": "VoiceGuidance", "responsibility": "Generate turn-by-turn voice instructions", "input": "Route, position", "output": "Audio output", "notes": ""},
            {"id": "SWE2-CMP-005", "component": "TrafficReceiver", "responsibility": "Receive and decode TMC traffic data", "input": "TMC signal", "output": "Traffic events", "notes": ""},
        ],
        "SWE.3": [
            {"id": "SWE3-FUN-001", "function": "CalcRoute", "input": "start (lat,lon), destination (lat,lon)", "output": "route_path (waypoints)", "description": "A* pathfinding on road network graph", "notes": ""},
            {"id": "SWE3-FUN-002", "function": "RenderMapTile", "input": "tile_id, zoom_level", "output": "pixel_buffer", "description": "Render vector map tile to pixel buffer", "notes": ""},
            {"id": "SWE3-FUN-003", "function": "UpdateGPSPosition", "input": "raw_gps_data", "output": "lat, lon, heading", "description": "GPS signal processing with Kalman filter", "notes": ""},
            {"id": "SWE3-FUN-004", "function": "GenerateGuidance", "input": "route, current_pos", "output": "audio_command", "description": "Determine next maneuver and generate TTS", "notes": ""},
        ],
        "SWE.4": [
            {"id": "SWE4-UT-001", "function": "CalcRoute", "test_desc": "Short route: 5km urban distance", "expected": "Route found in < 1s", "actual": "Route found in 0.8s", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-002", "function": "RenderMapTile", "test_desc": "Zoom level 15, urban area tile", "expected": "Tile rendered < 33ms", "actual": "Tile rendered in 28ms", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-003", "function": "UpdateGPSPosition", "test_desc": "Valid GPS signal with 5 satellites", "expected": "Position accuracy < 3m", "actual": "Position accuracy 2.1m", "result": "Pass", "notes": ""},
            {"id": "SWE4-UT-004", "function": "GenerateGuidance", "test_desc": "Approaching right turn in 200m", "expected": "Voice: Turn right in 200m", "actual": "Voice: Turn right in 200m", "result": "Pass", "notes": ""},
        ],
        "SWE.5": [
            {"id": "SWE5-IT-001", "interface": "GPSManager to MapRenderer", "test_desc": "GPS position to map display centering", "expected": "Map centers on GPS position", "actual": "Map centers on position", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-002", "interface": "RouteEngine to MapRenderer", "test_desc": "Route overlay on map display", "expected": "Route drawn correctly on map", "actual": "Route drawn correctly", "result": "Pass", "notes": ""},
            {"id": "SWE5-IT-003", "interface": "TrafficReceiver to RouteEngine", "test_desc": "Traffic data triggers route recalculation", "expected": "Route recalculated within 5s", "actual": "Route recalculated in 3.2s", "result": "Pass", "notes": ""},
        ],
        "SWE.6": [
            {"id": "SWE6-QT-001", "req_id": "SWE1-REQ-001", "test_desc": "GPS position accuracy qualification test", "expected": "Position accuracy < 3m", "actual": "Position accuracy 2.1m", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-002", "req_id": "SWE1-REQ-002", "test_desc": "Route calculation time for 500km route", "expected": "Route calculated within 5s", "actual": "Route calculated in 3.8s", "result": "Pass", "notes": ""},
            {"id": "SWE6-QT-003", "req_id": "SWE1-REQ-003", "test_desc": "Map display frame rate under load", "expected": "Minimum 30fps maintained", "actual": "Average 45fps, min 32fps", "result": "Pass", "notes": ""},
        ],
    }
    return data.get(swe_level)


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
                "SWE.1": [("Software Requirements Specification", "srs")],
                "SWE.2": [("Software Architecture Design", "sad")],
                "SWE.3": [("Software Detailed Design", "sdd")],
                "SWE.4": [("Unit Test Report", "ut_report")],
                "SWE.5": [("Integration Test Report", "it_report")],
                "SWE.6": [("Qualification Test Report", "qt_report")],
            }
            docs = [{"name": n, "template_id": t} for n, t in default_docs.get(swe_level, [])]

        swe_doc_ids = []
        for doc_info in docs:
            doc_name = doc_info.get("name", "Unnamed Document")
            template_id = doc_info.get("template_id", "")
            did = DocumentModel.create(stage_id, doc_name, template_type=template_id, conn=conn)
            swe_doc_ids.append(did)

            # Create JSON item-based content for demo documents
            content = _create_demo_items(project_name, oem_name, swe_level)
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
