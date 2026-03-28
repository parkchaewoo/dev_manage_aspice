# Software Integration Test Report / 소프트웨어 통합 시험 보고서

---
<!-- GUIDE: SWE.2 아키텍처 설계에 대해 통합된 소프트웨어를 시험하는 보고서입니다 -->

| Field / 항목 | Value / 값 |
|---|---|
| Project Name | {project_name} |
| OEM | {oem_name} |
| Document ID | {document_id} |
| Version | 0.1 |
| Date | {date} |
| Author | |
| Status | Draft |

## Input Artifacts / 입력 산출물
| Artifact | Source |
|---|---|
| SW Architecture Design (SWE.2) | SWE.2 |
| Unit Test Report (SWE.4) | SWE.4 |
| Verified SW Units | SWE.4 |

## Output Artifacts / 출력 산출물
| Artifact | Target |
|---|---|
| Integration Test Report (this) | SWE.6 Qualification |
| Integrated SW Build | SWE.6 Qualification |

---

## 1. Integration Strategy / 통합 전략
<!-- GUIDE: V-Model 쌍: SWE.2(아키텍처) ↔ SWE.5(통합시험) -->

- **Approach / 접근법**: Bottom-up integration
- **Rationale / 이유**: 하위 모듈부터 검증하여 인터페이스 결함 조기 발견

### Build Sequence / 빌드 순서

| Step | Components Integrated | Test Focus | Dependencies |
|---|---|---|---|
| 1 | SensorInput + ControlLogic | Data flow Sensor→Control | SensorInput unit tested |
| 2 | + ActuatorOutput | Full control chain | Step 1 passed |
| 3 | + CommManager | CAN signal integration | Step 2 passed |
| 4 | + SafetyMonitor | Safety state propagation | Step 3 passed |
| 5 | + DiagManager + NvmManager | Full system | Step 4 passed |

---

## 2. Test Environment / 시험 환경

| Item | Description |
|---|---|
| Test Platform | HIL (Hardware-in-the-Loop) / SIL (Software-in-the-Loop) |
| HIL Simulator | dSPACE SCALEXIO / ETAS LABCAR / Vector CANoe |
| Target ECU | Production ECU / Eval Board |
| CAN Simulation | Vector CANoe + .dbc file |
| Test Automation | Python + CANape / CAPL script |
| Signal Injection | HIL analog/digital I/O |

---

## 3. Interface Test Cases / 인터페이스 시험 항목

| TC-ID | Interface | Source→Target | Protocol | Expected | Actual | Result |
|---|---|---|---|---|---|---|
| IT-001 | SensorInput→ControlLogic | Steering angle data | Internal API | angle=45.0° received correctly | | |
| IT-002 | ControlLogic→ActuatorOutput | Torque command | Internal API | torque=5.0 Nm output within 5ms | | |
| IT-003 | CommManager→ControlLogic | Vehicle speed (CAN 0x123) | CAN 500kbps | Speed parsed correctly, 20ms cycle | | |
| IT-004 | SafetyMonitor→ControlLogic | Safety state change | Internal API | DEGRADED state reduces torque 50% | | |
| IT-005 | DiagManager→NvmManager | DTC write request | Internal API | DTC stored, CRC valid | | |
| IT-006 | CAN Tx: AssistTorque (0x200) | SW→CAN bus | CAN | Message cycle 5ms ±0.5ms | | |
| IT-007 | CAN Rx timeout | No CAN input >100ms | CAN | Timeout detected, safe defaults used | | |
| IT-008 | Sensor→Control→Actuator chain | End-to-end latency | Mixed | Total latency < 10ms | | |

---

## 4. Timing Verification / 타이밍 검증

| Path / 경로 | Deadline / 마감 | Measured / 측정값 | Margin / 여유 | Status |
|---|---|---|---|---|
| Main control loop (5ms task) | 5.0 ms | | | |
| Sensor read → Torque output | 5.0 ms | | | |
| CAN Rx → Processing complete | 10.0 ms | | | |
| Safety fault → Safe state | 10.0 ms | | | |
| Watchdog refresh | 50.0 ms | | | |
| Boot → Ready | 200 ms | | | |

---

## 5. Communication Protocol Test / 통신 프로토콜 시험

### 5.1 CAN Bus Test

| Test | Description | Expected | Result |
|---|---|---|---|
| Bus-off recovery | Simulate CAN bus-off | Recovery within 500ms | |
| Message loss | Drop 5 consecutive messages | Timeout detection | |
| Wrong DLC | Send message with wrong length | Message rejected | |
| Bus load test | 80% bus load | No message loss | |

### 5.2 Diagnostic Protocol (UDS)

| Service | Description | Expected | Result |
|---|---|---|---|
| 0x10 DiagSessionCtrl | Switch to Extended Session | Positive response | |
| 0x19 ReadDTCInfo | Read stored DTCs | DTC list returned | |
| 0x14 ClearDTC | Clear all DTCs | DTCs cleared, NVM updated | |
| 0x22 ReadDataByID | Read steering angle | Current value returned | |

---

## 6. Resource Measurement / 리소스 측정

| Module | Stack Usage (B) | Heap Usage (B) | CPU Load (%) | Budget | Status |
|---|---|---|---|---|---|
| Task_5ms | | | | 30% | |
| Task_10ms | | | | 15% | |
| Task_100ms | | | | 10% | |
| Total RAM | | | - | 70% of 64KB | |
| Total ROM | | | - | 80% of 256KB | |

---

## 7. Defect Summary / 결함 요약

| ID | TC-ID | Severity | Description | Root Cause | Status |
|---|---|---|---|---|---|
| INT-DEF-001 | IT-003 | (예시) CAN message byte order wrong | Endianness mismatch | Closed |
| | | | | | |

---

## 8. Traceability / 추적성 (SWE.2 → SWE.5)

| SWE.2 Architecture Element | IT Test Cases | Coverage |
|---|---|---|
| SensorInput→ControlLogic interface | IT-001 | Full |
| ControlLogic→ActuatorOutput interface | IT-002 | Full |
| CommManager→ControlLogic interface | IT-003 | Full |
| SafetyMonitor→All components | IT-004 | Full |
| DiagManager→NvmManager interface | IT-005 | Full |
| CAN message output | IT-006 | Full |
| CAN timeout handling | IT-007 | Full |
| End-to-end chain | IT-008 | Full |

---

## 9. Review Criteria / 검토 기준
| # | Criteria | Check |
|---|---|---|
| 1 | All SWE.2 interfaces tested | ☐ |
| 2 | Integration build sequence completed | ☐ |
| 3 | Timing requirements met | ☐ |
| 4 | Resource usage within budget | ☐ |
| 5 | No open critical defects | ☐ |
| 6 | CAN communication verified | ☐ |
| 7 | Traceability to SWE.2 complete | ☐ |

---
*Generated by ASPICE Process Manager*
