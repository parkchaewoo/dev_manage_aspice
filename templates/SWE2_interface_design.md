# Interface Design Document (IDD)
# 인터페이스 설계 문서

---

<!-- GUIDE: 이 문서는 소프트웨어 컴포넌트 간 및 외부 시스템과의 인터페이스를 정의합니다. -->
<!-- GUIDE: This document defines interfaces between SW components and external systems. -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name / 프로젝트명 | {project_name} |
| OEM | {oem_name} |
| Document ID / 문서 ID | {document_id} |
| Version / 버전 | 0.1 |
| Date / 작성일 | {date} |
| Author / 작성자 | |
| Reviewer / 검토자 | |
| Approval / 승인자 | |
| Status / 상태 | Draft |
| Classification / 기밀등급 | Confidential |

---

## Revision History / 개정 이력

| Version | Date | Author | Description / 설명 |
|---------|------|--------|-------------------|
| 0.1 | {date} | | Initial draft / 초안 작성 |
| | | | |

---

## 1. Introduction / 소개

### 1.1 Purpose / 목적
본 문서는 {project_name} 프로젝트의 소프트웨어 인터페이스를 정의합니다.
This document defines the software interfaces for the {project_name} project.

### 1.2 Scope / 범위
- CAN Communication Interface / CAN 통신 인터페이스
- Sensor Input Interface / 센서 입력 인터페이스
- Actuator Output Interface / 액추에이터 출력 인터페이스
- Inter-SWC Interface / SWC 간 인터페이스
- Diagnostic Interface / 진단 인터페이스

---

## 2. CAN Message Specification / CAN 메시지 사양

### 2.1 Transmitted Messages / 송신 메시지

| Msg Name / 메시지명 | CAN ID | DLC | Cycle / 주기 | Signal List / 신호 목록 | Timeout / 타임아웃 |
|---|---|---|---|---|---|
| EPS_Status | 0x200 | 8 | 10 ms | AssistTorque, SystemMode, FaultFlag | 50 ms |
| EPS_Diag | 0x201 | 8 | 100 ms | DTCCount, ActiveDTC, LifeCounter | 500 ms |
| | (메시지를 추가하세요 / Add messages) | | | | |

### 2.2 Received Messages / 수신 메시지

| Msg Name / 메시지명 | CAN ID | DLC | Cycle / 주기 | Signal List / 신호 목록 | Timeout / 타임아웃 |
|---|---|---|---|---|---|
| VCU_Control | 0x100 | 8 | 10 ms | SteeringAngle, VehicleSpeed, IgnSts | 50 ms |
| VCU_Info | 0x123 | 8 | 20 ms | EngineRPM, BrakeStatus, GearPos | 100 ms |
| | (메시지를 추가하세요 / Add messages) | | | | |

---

## 3. Signal Specification / 신호 사양

| Signal Name / 신호명 | Message | Byte Pos | Bit Pos | Length | Data Type | Factor | Offset | Min | Max | Unit | Init Value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SteeringAngle | VCU_Control | 0-1 | 0 | 16 | INT16 | 0.1 | 0 | -7200 | 7200 | deg | 0 |
| VehicleSpeed | VCU_Control | 2-3 | 0 | 16 | UINT16 | 0.01 | 0 | 0 | 3000 | km/h | 0 |
| AssistTorque | EPS_Status | 0-1 | 0 | 16 | INT16 | 0.01 | 0 | -1200 | 1200 | Nm | 0 |
| SystemMode | EPS_Status | 2 | 0 | 8 | UINT8 | 1 | 0 | 0 | 7 | - | 0 |
| FaultFlag | EPS_Status | 3 | 0 | 8 | UINT8 | 1 | 0 | 0 | 255 | - | 0 |
| | (신호를 추가하세요 / Add signals) | | | | | | | | | | |

---

## 4. Sensor Interface / 센서 인터페이스

| Sensor / 센서 | HW Interface | Pin | Sampling Rate | Resolution | Range | Accuracy | Filter |
|---|---|---|---|---|---|---|---|
| Steering Angle Sensor | SPI (Ch0) | P3.0-P3.3 | 1 kHz | 0.1 deg | +-720 deg | +-0.5 deg | Moving Avg (N=4) |
| Torque Sensor | ADC (Ch1) | P4.0 | 2 kHz | 12-bit | +-10 Nm | +-0.05 Nm | Low-pass 100Hz |
| Motor Current Sensor | ADC (Ch2) | P4.1 | 10 kHz | 12-bit | 0-80 A | +-0.5 A | Low-pass 1kHz |
| Temperature Sensor | ADC (Ch3) | P4.2 | 10 Hz | 10-bit | -40~150 C | +-2 C | Moving Avg (N=8) |

---

## 5. Actuator Interface / 액추에이터 인터페이스

| Actuator / 구동기 | HW Interface | Pin | Control Method | Range | Resolution | Safety Cutoff |
|---|---|---|---|---|---|---|
| EPS Motor | PWM (20kHz) | P5.0-P5.1 | Current Control | 0-100% duty | 0.1% | HW Watchdog |
| Warning Lamp | GPIO | P6.0 | On/Off | - | - | - |
| Power Relay | GPIO | P6.1 | On/Off | - | - | Independent monitor |

---

## 6. Inter-Component Interface / 컴포넌트 간 인터페이스

| Sender SWC | Receiver SWC | Port Name | Data Element | Data Type | Unit | Update Rate |
|---|---|---|---|---|---|---|
| SWC_SensorProc | SWC_TorqueCalc | PP_SteerAngle | SteeringAngle_deg | FLOAT32 | deg | 1 kHz |
| SWC_SensorProc | SWC_SafetyMon | PP_SensorStatus | SensorValid_flag | BOOLEAN | - | 1 kHz |
| SWC_TorqueCalc | SWC_MotorCtrl | PP_TorqueCmd | TargetTorque_Nm | FLOAT32 | Nm | 1 kHz |
| SWC_SafetyMon | SWC_MotorCtrl | PP_SafeState | SafeStateCmd | UINT8 | - | 1 kHz |
| SWC_Diag | SWC_NvmMgr | PP_DTCWrite | DTCRecord | STRUCT | - | Event |

---

## 7. Diagnostic Interface / 진단 인터페이스

### 7.1 UDS Services / UDS 서비스

| Service ID | Service Name | Sub-Function | Description / 설명 |
|---|---|---|---|
| 0x10 | DiagnosticSessionControl | 0x01, 0x02, 0x03 | 세션 제어 |
| 0x11 | ECUReset | 0x01 | ECU 리셋 |
| 0x14 | ClearDiagnosticInformation | - | DTC 클리어 |
| 0x19 | ReadDTCInformation | 0x01, 0x02, 0x06 | DTC 읽기 |
| 0x22 | ReadDataByIdentifier | - | 데이터 읽기 |
| 0x2E | WriteDataByIdentifier | - | 데이터 쓰기 |
| 0x31 | RoutineControl | - | 루틴 제어 |

---

## 8. Review Criteria / 검토 기준

| # | Criteria / 기준 | Check |
|---|---|---|
| 1 | All CAN messages fully specified / 모든 CAN 메시지 완전 명세 | ☐ |
| 2 | Signal byte order and bit position correct / 신호 바이트 순서 및 비트 위치 정확 | ☐ |
| 3 | Timeout values defined for all messages / 모든 메시지에 타임아웃 정의 | ☐ |
| 4 | Sensor accuracy and range consistent with HW spec / 센서 정확도 및 범위가 HW 사양과 일치 | ☐ |
| 5 | Inter-SWC interfaces consistent with architecture / SWC 간 인터페이스가 아키텍처와 일치 | ☐ |
| 6 | Diagnostic services comply with {oem_name} standard / 진단 서비스가 OEM 표준 준수 | ☐ |
| 7 | All data types and units specified / 모든 데이터 타입 및 단위 명시 | ☐ |
| 8 | Safety-relevant interfaces identified / 안전 관련 인터페이스 식별됨 | ☐ |

---

## 9. Review History / 검토 이력

| Date / 날짜 | Reviewer / 검토자 | Result / 결과 | Comments / 비고 |
|---|---|---|---|
| | | Approved / Rejected | |

---

*Generated by ASPICE Process Manager*
